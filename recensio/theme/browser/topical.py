import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.solr.browser.facets import SearchFacetsView
from Products.Archetypes.utils import OrderedDict
from zope.component import queryUtility
from collective.solr.interfaces import ISolrConnectionConfig
from collective.solr.browser.facets import param
from copy import deepcopy
from ZTUtils import make_query
#from recensio.contenttypes.config import PORTAL_TYPES
from recensio.policy.utility import getSelectedQuery, \
    convertFacets, browsing_facets as facet_fields

log = logging.getLogger('recensio.theme/topical.py')
PORTAL_TYPES = ['Presentation Online Resource', 'Presentation Article Review',
    'Presentation Collection', 'Presentation Monograph',
        'Review Journal', 'Review Monograph' ]


class BrowseTopicsView(SearchFacetsView):
    """View for topical browsing (ddcPlace etc.)
    """

    def __init__(self, context, request):
        catalog = getToolByName(context, 'portal_catalog')
        self.default_query = {'portal_type': PORTAL_TYPES,
                              'facet': 'true', 
                              'facet.field': facet_fields }
        BrowserView.__init__(self, context, request)

    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        query = self.default_query.copy()
        form = self.request.form
        if 'fq' in form:
            # filter out everything but our ddc attributes
            form['fq'] = [x for x in form['fq'] if x.split(':')[0].strip('+') in facet_fields]
        self.form = form
        query.update(self.form)
        catalog = getToolByName(self.context, 'portal_catalog')
        self.results = catalog(query)
        if not self.kw.has_key('results'):
            self.kw['results'] = self.results
        return super(BrowseTopicsView, self).__call__(*args, **kw)

    def getResults(self):
        return self.results or self.kw['results']

    def getUsedFacets(self):
        fq = self.request.get('fq', [])
        if isinstance(fq, basestring):
            fq = [fq]
        used = set([facet.split(':', 1)[0].strip('+') for facet in fq])
        used = used.intersection(set(facet_fields))
        return tuple(used)

    def facets(self):
        """ prepare and return facetting info for the given SolrResponse """
        results = self.kw.get('results', None)
        fcs = getattr(results, 'facet_counts', None)
        if results is not None and fcs is not None:
            filt = None # lambda name, count: name and count > 0
            if 'fq' in self.form:
                # filter out everything but our ddc attributes
                self.form['fq'] = [x for x in self.form['fq'] if x.split(':')[0].strip('+') in facet_fields]
            return convertFacets(fcs.get('facet_fields', {}),
                self.context, self.form, filt)
        else:
            return None
        if results is not None: # we have no facet information, solr probably not running
            filt = None
            catalog = getToolByName(self.context, 'portal_catalog')
            indexes = filter(lambda i: i.id in facet_fields, catalog.getIndexObjects())
            # I know this is sick, but it shouldn't get used anyway
            ffdict = dict(map(lambda ind: (ind.id, dict(map(lambda x: (x, 1), [item for sublist in ind.uniqueValues() for item in sublist] ))), indexes))
            return convertFacets(ffdict,
                self.context, self.form, filt)

    def selected(self):
        """ determine selected facets and prepare links to clear them;
            this assumes that facets are selected using filter queries """
        info = []
        facets = param(self, 'facet.field')
        fq = param(self, 'fq')
        fq = [x for x in fq]
        fq = filter(lambda x: x.split(':')[0].strip('+') in facet_fields, fq)
        form = self.form
        for idx, query in enumerate(fq):
            field, value = query.split(':', 1)
            params = self.form.copy()
            params['fq'] = fq[:idx] + fq[idx+1:]
            if field not in facets:
                params['facet.field'] = facets + [field]
            if value.startswith('"') and value.endswith('"'):
                info.append(dict(title=field, value=value[1:-1],
                    query=make_query(params), doseq=True))
        return info


    def getMenu(self):
        voc = getToolByName(self.context, 'portal_vocabularies', None)
        if not voc:
            return dict(ddcPlace=[], ddcTime=[], ddcSubject=[])
        vocDict = dict()
        vocDict['ddcPlace'] = voc.getVocabularyByName('region_values').getVocabularyDict(voc)
        vocDict['ddcTime'] = voc.getVocabularyByName('epoch_values').getVocabularyDict(voc)
        vocDict['ddcSubject'] = voc.getVocabularyByName('topic_values').getVocabularyDict(voc)

        facets = self.facets()
        selected = self.selected()
        
        def getSubmenu(vocab, facet, selected):
            submenu = []
            for item in vocab.items():
                # extract vocabulary term for item
                itemvoc = item[0]
                if isinstance(item[1], basestring):
                    itemvoc = item[1]
                elif isinstance(item[1], tuple):
                    itemvoc = item[1][0]

                iteminfo = dict(name=item[0], voc=itemvoc, count=0, query='', submenu=[])
                # look if we have info from facets()
                if facet:
                    facetinfo = filter(lambda x: x['name'] == item[0], facet['counts'])
                    if facetinfo: # and facetinfo[0]['count'] > 0:
                        iteminfo.update(facetinfo[0])
                # look if we have info from selected()
                if selected:
                    selectedinfo = filter(lambda x: x['value'] == item[0], selected)
                    if selectedinfo:
                        iteminfo['clearquery'] = selectedinfo[0]['query']
                        log.debug('selected %(value)s for %(title)s' % selectedinfo[0])

                # recurse if we have subordinate vocabulary items
                if isinstance(item[1][1], dict) or isinstance(item[1][1], OrderedDict):
                    subsubmenu = getSubmenu(item[1][1], facet, selected)
                    iteminfo['submenu'] = subsubmenu
                    #iteminfo['count'] += sum(map(lambda x: x['count'], subsubmenu))

                submenu.append(iteminfo)

            return submenu

        menu = dict()

        for attrib in facet_fields:
            submenu = []
            if facets:
                facets_sub = filter(lambda x: x['title'] == attrib, facets)
            else:
                facets_sub = []
            if selected:
                selected_sub = filter(lambda x: x['title'] == attrib, selected)
            else:
                selected_sub = []

            if facets_sub:
                facets_sub = facets_sub[0]
            if facets_sub or selected_sub:
                submenu = getSubmenu(vocDict[attrib], facets_sub, selected_sub)
            menu[attrib] = submenu
        return menu

    def getSubmenus(self):
        menu = self.getMenu()
        # this would work if ATVocabularyManager.utils were consistent:
        # submenus = [dict(title=voc.getVocabularyByName('region_values').Title(),id='ddcPlace'),
        submenus = [dict(title='Region',id='ddcPlace'), 
                    dict(title='Epoch',id='ddcTime'), 
                    dict(title='Topic', id='ddcSubject')
                   ]
                   
        for submenu in submenus:
            mid = submenu['id']
            cq = [item for item in menu[mid] if item.has_key('clearquery')]
            for item in menu[mid]:
                cq = cq + [subitem for subitem in item['submenu'] if subitem.has_key('clearquery')]
            submenu['selected'] = cq
        
        return submenus
        
    def showSubmenu(self, submenu):
        """Returns True if submenu has an entry with query or clearquery set, 
            i.e. should be displayed
        """
        return not filter(lambda x: x.has_key('clearquery') or x['count']>0, submenu) == []

    def expandSubmenu(self, submenu):
        """Returns True if submenu has an entry with clearquery set, i.e.
           should be displayed expanded
        """
        return not filter(lambda x: x.has_key('clearquery'), submenu) == []
