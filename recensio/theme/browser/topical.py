import logging
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from collective.solr.browser.facets import convertFacets, SearchFacetsView
from Products.Archetypes.utils import OrderedDict

log = logging.getLogger('recensio.theme/topical.py')

class BrowseTopicsView(SearchFacetsView):
    """View for topical browsing (ddcPlace etc.)
    """

    def __init__(self, context, request):
        self.default_query = {'facet': 'true', 
                              'facet.field': ['ddcPlace', 'ddcTime', 'ddcSubject']}
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

    def facets(self):
        """ prepare and return facetting info for the given SolrResponse """
        results = self.kw.get('results', None)
        fcs = getattr(results, 'facet_counts', None)
        if results is not None and fcs is not None:
            filter = None # lambda name, count: name and count > 0
            return convertFacets(fcs.get('facet_fields', {}),
                self.context, self.request.form, filter)
        else:
            return None

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
        return not filter(lambda x: x.has_key('clearquery') or x['query'], submenu) == []

    def expandSubmenu(self, submenu):
        """Returns True if submenu has an entry with clearquery set, i.e.
           should be displayed expanded
        """
        return not filter(lambda x: x.has_key('clearquery'), submenu) == []
