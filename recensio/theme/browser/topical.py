from copy import deepcopy
from traceback import format_stack
import logging

from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from ZTUtils import make_query
from zope.component import queryUtility

from Products.Archetypes.utils import OrderedDict
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from collective.solr.browser.facets import (
    SearchFacetsView, param)
from collective.solr.interfaces import ISolrConnectionConfig
from plone.memoize import instance
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.component.hooks import setSite

#from recensio.contenttypes.config import PORTAL_TYPES
from recensio.policy.interfaces import IRecensioSettings
from recensio.policy.utility import getSelectedQuery, \
    convertFacets, browsing_facets

log = logging.getLogger('recensio.theme/topical.py')
PORTAL_TYPES = ['Presentation Online Resource', 'Presentation Article Review',
    'Presentation Collection', 'Presentation Monograph',
        'Review Journal', 'Review Monograph' ]


class SwitchPortal(object):
    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        self.original_portal = getSite()
        setSite(self.portal)

    def __exit__(self, type, value, traceback):
        setSite(self.original_portal)
        if value:
            log.warn('Could not get portal url of ' + self.portal.id,
                      exc_info=(type, value, traceback))
            return True


class BrowseTopicsView(SearchFacetsView):
    """View for topical browsing (ddcPlace etc.)
    """
    show_if_empty = False

    def __init__(self, context, request):
        self.facet_fields = browsing_facets
        self.default_query = {'portal_type': PORTAL_TYPES,
                              'facet': 'true',
                              'facet.field': self.facet_fields,
                              'b_size': 10,
                              'b_start': 0, }

        voc = getToolByName(context, 'portal_vocabularies', None)
        if not voc:
            return dict(ddcPlace=[], ddcTime=[], ddcSubject=[])
        self.vocDict = dict()
        self.vocDict['ddcPlace'] = voc.getVocabularyByName(
            'region_values').getVocabularyDict(voc)
        self.vocDict['ddcTime'] = voc.getVocabularyByName(
            'epoch_values').getVocabularyDict(voc)
        self.vocDict['ddcSubject'] = voc.getVocabularyByName(
            'topic_values').getVocabularyDict(voc)

        self.submenus = [
            dict(title='Epoch',id='ddcTime'),
            dict(title='Region',id='ddcPlace'),
            dict(title='Topic', id='ddcSubject')]

        self.queryparam = 'fq'

        BrowserView.__init__(self, context, request)

    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        query = self.default_query.copy()
        form = self.request.form
        if self.queryparam in form:
            # filter out everything but our ddc attributes
            if self.queryparam == 'fq':
                form[self.queryparam] = [
                    x for x in form[self.queryparam]
                    if x.split(':')[0].strip('+') in self.facet_fields]
        self.form = form
        query.update(self.form)
        if 'set_language' in query:
            del(query['set_language'])
        for key in query.keys():
            if query[key] == '':
                del(query[key])
        if form.get('use_navigation_root', True) and 'path' not in query:
            query['path'] = getNavigationRoot(self.context)
        catalog = getToolByName(self.context, 'portal_catalog')
        self.results = catalog(query)
        self.kw['results'] = self.results
        return super(BrowseTopicsView, self).__call__(*args, **kw)

    def getResults(self):
        return self.results or self.kw['results']

    def getUsedFacets(self):
        fq = self.request.get(self.queryparam, [])
        if isinstance(fq, basestring):
            fq = [fq]
        used = set([facet.split(':', 1)[0].strip('+') for facet in fq])
        used = used.intersection(set(self.facet_fields))
        return tuple(used)

    def facets(self):
        """ prepare and return facetting info for the given SolrResponse """
        results = self.kw.get('results', None)
        fcs = getattr(results, 'facet_counts', None)
        if results is not None and fcs is not None:
            filt = None # lambda name, count: name and count > 0
            if self.queryparam in self.form:
                if self.queryparam == 'fq':
                    container = self.form[self.queryparam]
                else:
                    container = self.form
                # filter out everything but our ddc attributes
                if self.queryparam == 'fq':
                    self.form[self.queryparam] = [
                        x for x in self.form[self.queryparam]
                        if x.split(':')[0].strip('+') in self.facet_fields]
            return convertFacets(fcs.get('facet_fields', {}),
                self.context, self.form, filt, facet_fields=self.facet_fields, queryparam=self.queryparam)
        else:
            return None
        if results is not None:
            # we have no facet information, solr probably not running
            filt = None
            catalog = getToolByName(self.context, 'portal_catalog')
            indexes = filter(
                lambda i: i.id in self.facet_fields, catalog.getIndexObjects())
            # I know this is sick, but it shouldn't get used anyway
            ffdict = dict(
                map(lambda ind: (
                        ind.id,
                        dict(
                            map(lambda x: (x, 1),
                                [item for sublist in ind.uniqueValues()
                                 for item in sublist]
                                )
                            )
                        ),
                    indexes)
                )
            return convertFacets(ffdict,
                self.context, self.form, filt,
                facet_fields=self.facet_fields, queryparam=self.queryparam)

    def selected(self):
        """ determine selected facets and prepare links to clear them;
            this assumes that facets are selected using filter queries """
        info = []
        facets = param(self, 'facet.field')
        fq = param(self, self.queryparam)
        fq = [x for x in fq]
        if self.queryparam == 'fq':
            fq = filter(lambda x: x.split(':')[0].strip('+') in self.facet_fields, fq)
        form = self.form
        for idx, query in enumerate(fq):
            params = self.form.copy()
            if self.queryparam == 'fq':
                field, value = query.split(':', 1)
            else:
                field = self.queryparam
                value = '"%s"' % query
            params[self.queryparam] = fq[:idx] + fq[idx+1:]
            if field not in facets:
                params['facet.field'] = facets + [field]
            if value.startswith('"') and value.endswith('"'):
                info.append(dict(title=field, value=value[1:-1],
                    query=make_query(params, doseq=True)))
        return info


    def sort(self, submenu):
        return sorted(submenu, key=lambda x:x['count'], reverse=True)

    def getMenu(self):
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

                iteminfo = dict(
                    name=item[0], voc=itemvoc, count=0, query='', submenu=[])
                # look if we have info from facets()
                if facet:
                    facetinfo = filter(
                        lambda x: x['name'] == item[0], facet['counts'])
                    if facetinfo: # and facetinfo[0]['count'] > 0:
                        iteminfo.update(facetinfo[0])
                # look if we have info from selected()
                if selected:
                    selectedinfo = filter(
                        lambda x: x['value'] == item[0], selected)
                    if selectedinfo:
                        iteminfo['clearquery'] = selectedinfo[0]['query']
                        log.debug('selected %(value)s for %(title)s'
                                  % selectedinfo[0])

                # recurse if we have subordinate vocabulary items
                if isinstance(item[1][1], dict) or \
                        isinstance(item[1][1], OrderedDict):
                    subsubmenu = getSubmenu(item[1][1], facet, selected)
                    iteminfo['submenu'] = subsubmenu
                    # iteminfo['count'] += sum(map(
                    #         lambda x: x['count'], subsubmenu))

                submenu.append(iteminfo)

            return self.sort(submenu)

        menu = dict()

        for attrib in self.facet_fields:
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
            if facets_sub or selected_sub or self.show_if_empty:
                submenu = getSubmenu(self.vocDict[attrib], facets_sub, selected_sub)
            menu[attrib] = submenu
        return menu

    def getSubmenus(self):
        menu = self.getMenu()
        # this would work if ATVocabularyManager.utils were consistent:
        # submenus = [dict(title=voc.getVocabularyByName('region_values').
        #                  Title(),id='ddcPlace'),
        submenus = self.submenus
        for submenu in submenus:
            mid = submenu['id']
            cq = [item for item in menu[mid]
                  if item.has_key('clearquery')]
            for item in menu[mid]:
                cq = cq + [subitem for subitem in item['submenu']
                           if subitem.has_key('clearquery')]
            submenu['selected'] = cq

        return submenus

    def showSubmenu(self, submenu):
        """Returns True if submenu has an entry with query or clearquery set,
            i.e. should be displayed
        """
        return not filter(lambda x: x.has_key('clearquery')
                          or x['count']>0, submenu) == []

    def expandSubmenu(self, submenu):
        """Returns True if submenu has an entry with clearquery set, i.e.
           should be displayed expanded
        """
        return not filter(lambda x: x.has_key('clearquery') or
                          self.expandSubmenu(x['submenu']), submenu) == [
]

    def get_toggle_cross_portal_url(self):
        new_form = self.request.form.copy()
        new_form['use_navigation_root'] = not new_form.get('use_navigation_root', True)
        return '?'.join((self.request['ACTUAL_URL'], make_query(new_form)))

    @instance.memoize
    def get_foreign_portal_url(self, portal_id):
        other_portal = self.context.unrestrictedTraverse('/' + portal_id)
        external_url = None
        with SwitchPortal(other_portal):
            registry = getUtility(IRegistry)
            recensio_settings = registry.forInterface(IRecensioSettings)
            external_url = recensio_settings.external_portal_url
        return external_url

    def get_foreign_url(self, result):
        portal_id = result.getPath().split('/')[1]
        other_portal = self.context.unrestrictedTraverse('/' + portal_id)
        external_url = self.get_foreign_portal_url(portal_id)
        if not external_url:
            return result.getURL()
        return result.getURL().replace(
            other_portal.absolute_url(), external_url)

    @instance.memoize
    def get_all_portal_ids(self):
        this_portal = getSite()
        app = aq_parent(this_portal)
        return app.objectIds('Plone Site')

    def get_portal_link_snippet(self):
        portal_ids = self.get_all_portal_ids()
        link_tpl = '<a href="{1}">{0}</a>'
        portal_infos = []
        for portal_id in portal_ids:
            portal_title = self.context.restrictedTraverse('/' + portal_id).Title()
            portal_infos.append(
                (portal_title, self.get_foreign_portal_url(portal_id)))
        link_snippet = ', '.join([
            link_tpl.format(*portal_info) for portal_info in portal_infos
            if portal_info[1]])
        return link_snippet
