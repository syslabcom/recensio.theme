import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.solr.browser.facets import convertFacets, SearchFacetsView
from Products.Archetypes.utils import OrderedDict
from zope.component import queryUtility
from collective.solr.interfaces import ISolrConnectionConfig
from collective.solr.browser.facets import param, facetParameters
from copy import deepcopy
from ZTUtils import make_query

log = logging.getLogger('recensio.theme/topical.py')

facet_fields = ['ddcPlace', 'ddcTime', 'ddcSubject']

def facetParameters(context, request):
    """ determine facet fields to be queried for """
    marker = []
    fields = request.get('facet.field', request.get('facet_field', marker))
    if isinstance(fields, basestring):
        fields = [fields]
    if fields is marker:
        fields = getattr(context, 'facet_fields', marker)
    if fields is marker:
        fields = facet_fields
    dependencies = {}
    for idx, field in enumerate(fields):
        if ':' in field:
            facet, dep = map(strip, field.split(':', 1))
            dependencies[facet] = map(strip, dep.split(','))
    return fields, dependencies

def convertFacets(fields, context=None, request={}, filter=None):
    """ convert facet info to a form easy to process in templates """
    info = []
    params = request.copy()   # request needs to be a dict, i.e. request.form
    facets, dependencies = list(facetParameters(context, request))
    params['facet.field'] = facets = list(facets)
    fq = params.get('fq', [])
    if isinstance(fq, basestring):
        fq = params['fq'] = [fq]
    selected = set([facet.split(':', 1)[0] for facet in fq ])
    for field, values in fields.items():
        counts = []
        second = lambda a, b: cmp(b[1], a[1])
        for name, count in sorted(values.items(), cmp=second):
            p = deepcopy(params)
            p.setdefault('fq', []).append('%s:"%s"' % (field, name.encode('utf-8')))
            #if field in p.get('facet.field', []):
            #    p['facet.field'].remove(field)
            if filter is None or filter(name, count):
                counts.append(dict(name=name, count=count,
                    query=make_query(p, doseq=True)))
        deps = dependencies.get(field, None)
        visible = deps is None or selected.intersection(deps)
        if counts and visible:
            info.append(dict(title=field, counts=counts))
    if facets:          # sort according to given facets (if available)
        def pos(item):
            try:
                return facets.index(item)
            except ValueError:
                return len(facets)      # position the item at the end
        func = lambda a, b: cmp(pos(a), pos(b))
    else:               # otherwise sort by title
        func = lambda a, b: cmp(a['title'], b['title'])
    return sorted(info, cmp=func)


class BrowseTopicsView(SearchFacetsView):
    """View for topical browsing (ddcPlace etc.)
    """

    def __init__(self, context, request):
        catalog = getToolByName(context, 'portal_catalog')
        types = [x for x in catalog.uniqueValuesFor('portal_type') if x not in ('Topic', 'Folder', 'Document')]
        self.default_query = {'portal_type': types,
                              'facet': 'true', 
                              'facet.field': facet_fields }
        BrowserView.__init__(self, context, request)

    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        query = self.default_query.copy()
        query.update(self.request.form)
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
            fq = params['fq'] = [fq]
        used = set([facet.split(':', 1)[0] for facet in fq if facet[0]!='+'])
        return tuple(used)

    def facets(self):
        """ prepare and return facetting info for the given SolrResponse """
        results = self.kw.get('results', None)
        fcs = getattr(results, 'facet_counts', None)
        if results is not None and fcs is not None:
            filt = None # lambda name, count: name and count > 0
            return convertFacets(fcs.get('facet_fields', {}),
                self.context, self.request.form, filt)
        else:
            return None
        if results is not None: # we have no facet information, solr probably not running
            filt = None
            catalog = getToolByName(self.context, 'portal_catalog')
            indexes = filter(lambda i: i.id in facet_fields, catalog.getIndexObjects())
            # I know this is sick, but it shouldn't get used anyway
            ffdict = dict(map(lambda ind: (ind.id, dict(map(lambda x: (x, 1), [item for sublist in ind.uniqueValues() for item in sublist] ))), indexes))
            return convertFacets(ffdict,
                self.context, self.request.form, filt)

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

        for attrib in ['ddcPlace', 'ddcTime', 'ddcSubject']:
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
