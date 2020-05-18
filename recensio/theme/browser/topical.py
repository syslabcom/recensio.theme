import logging

from collective.solr.browser.facets import SearchFacetsView
from collective.solr.browser.facets import param
from Products.Archetypes.utils import OrderedDict
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.Five.browser import BrowserView
from recensio.contenttypes.config import REVIEW_TYPES
from recensio.policy.utility import browsing_facets
from recensio.policy.utility import convertFacets
from recensio.theme.browser.views import CrossPlatformMixin
from ZTUtils import make_query

log = logging.getLogger("recensio.theme/topical.py")
PORTAL_TYPES = REVIEW_TYPES


class BrowseTopicsView(SearchFacetsView, CrossPlatformMixin):
    """View for topical browsing (ddcPlace etc.)
    """

    show_if_empty = False

    def __init__(self, context, request):
        self.facet_fields = browsing_facets
        self.default_query = {
            "portal_type": PORTAL_TYPES,
            "facet": "true",
            "facet.field": self.facet_fields,
            "b_size": 10,
            "b_start": 0,
        }

        voc = getToolByName(context, "portal_vocabularies", None)
        if not voc:
            return dict(ddcPlace=[], ddcTime=[], ddcSubject=[])
        self.vocDict = dict()
        self.vocDict["ddcPlace"] = voc.getVocabularyByName(
            "region_values"
        ).getVocabularyDict(voc)
        self.vocDict["ddcTime"] = voc.getVocabularyByName(
            "epoch_values"
        ).getVocabularyDict(voc)
        self.vocDict["ddcSubject"] = voc.getVocabularyByName(
            "topic_values"
        ).getVocabularyDict(voc)

        self.submenus = [
            dict(title="Epoch", id="ddcTime"),
            dict(title="Region", id="ddcPlace"),
            dict(title="Topic", id="ddcSubject"),
        ]

        self.queryparam = "fq"

        BrowserView.__init__(self, context, request)

    def __call__(self, *args, **kw):
        self.args = args
        self.kw = kw
        query = self.default_query.copy()
        form = self.request.form
        if self.queryparam in form:
            # filter out everything but our ddc attributes
            if self.queryparam == "fq":
                form[self.queryparam] = [
                    x
                    for x in form[self.queryparam]
                    if x.split(":")[0].strip("+") in self.facet_fields
                ]
        form["facet.field"] = list(set(form.get("facet.field", []) + self.facet_fields))
        self.form = form
        query.update(self.form)
        if "set_language" in query:
            del query["set_language"]
        for key in query.keys():
            if query[key] in ["", []]:
                del query[key]
        if form.get("use_navigation_root", True) and "path" not in query:
            query["path"] = getNavigationRoot(self.context)
        catalog = getToolByName(self.context, "portal_catalog")
        self.results = catalog(query)
        self.kw["results"] = self.results
        return super(BrowseTopicsView, self).__call__(*args, **kw)

    def getResults(self):
        return self.results or self.kw["results"]

    def getUsedFacets(self):
        fq = self.request.get(self.queryparam, [])
        if isinstance(fq, basestring):
            fq = [fq]
        used = set([facet.split(":", 1)[0].strip("+") for facet in fq])
        used = used.intersection(set(self.facet_fields))
        return tuple(used)

    def facets(self):
        """ prepare and return facetting info for the given SolrResponse """
        results = self.kw.get("results", None)
        fcs = getattr(results, "facet_counts", None)
        if results is not None and fcs is not None:
            filt = None  # lambda name, count: name and count > 0
            if self.queryparam in self.form:
                if self.queryparam == "fq":
                    container = self.form[self.queryparam]
                else:
                    container = self.form
                # filter out everything but our ddc attributes
                if self.queryparam == "fq":
                    self.form[self.queryparam] = [
                        x
                        for x in self.form[self.queryparam]
                        if x.split(":")[0].strip("+") in self.facet_fields
                    ]
            return convertFacets(
                fcs.get("facet_fields", {}),
                self.context,
                self.form,
                filt,
                facet_fields=self.facet_fields,
                queryparam=self.queryparam,
            )
        else:
            return None
        if results is not None:
            # we have no facet information, solr probably not running
            filt = None
            catalog = getToolByName(self.context, "portal_catalog")
            indexes = filter(
                lambda i: i.id in self.facet_fields, catalog.getIndexObjects()
            )
            # I know this is sick, but it shouldn't get used anyway
            ffdict = dict(
                map(
                    lambda ind: (
                        ind.id,
                        dict(
                            map(
                                lambda x: (x, 1),
                                [
                                    item
                                    for sublist in ind.uniqueValues()
                                    for item in sublist
                                ],
                            )
                        ),
                    ),
                    indexes,
                )
            )
            return convertFacets(
                ffdict,
                self.context,
                self.form,
                filt,
                facet_fields=self.facet_fields,
                queryparam=self.queryparam,
            )

    def selected(self):
        """ determine selected facets and prepare links to clear them;
            this assumes that facets are selected using filter queries """
        info = []
        facets = param(self, "facet.field")
        fq = param(self, self.queryparam)
        fq = [x for x in fq]
        if self.queryparam == "fq":
            fq = filter(lambda x: x.split(":")[0].strip("+") in self.facet_fields, fq)
        form = self.form
        for idx, query in enumerate(fq):
            params = self.form.copy()
            if self.queryparam == "fq":
                field, value = query.split(":", 1)
            else:
                field = self.queryparam
                value = '"%s"' % query
            params[self.queryparam] = fq[:idx] + fq[idx + 1 :]
            if field not in facets:
                params["facet.field"] = facets + [field]
            if value.startswith('"') and value.endswith('"'):
                info.append(
                    dict(
                        title=field,
                        value=value[1:-1],
                        query=make_query(params, doseq=True),
                    )
                )
        return info

    def sort(self, submenu):
        return sorted(submenu, key=lambda x: x["count"], reverse=True)

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
                    name=item[0], voc=itemvoc, count=0, query="", submenu=[]
                )
                # look if we have info from facets()
                if facet:
                    facetinfo = filter(lambda x: x["name"] == item[0], facet["counts"])
                    if facetinfo:  # and facetinfo[0]['count'] > 0:
                        iteminfo.update(facetinfo[0])
                # look if we have info from selected()
                if selected:
                    selectedinfo = filter(lambda x: x["value"] == item[0], selected)
                    if selectedinfo:
                        iteminfo["clearquery"] = selectedinfo[0]["query"]
                        log.debug("selected %(value)s for %(title)s" % selectedinfo[0])

                # recurse if we have subordinate vocabulary items
                if isinstance(item[1][1], dict) or isinstance(item[1][1], OrderedDict):
                    subsubmenu = getSubmenu(item[1][1], facet, selected)
                    iteminfo["submenu"] = subsubmenu
                    # iteminfo['count'] += sum(map(
                    #         lambda x: x['count'], subsubmenu))

                submenu.append(iteminfo)

            return self.sort(submenu)

        menu = dict()

        for attrib in self.facet_fields:
            submenu = []
            if facets:
                facets_sub = filter(lambda x: x["title"] == attrib, facets)
            else:
                facets_sub = []
            if selected:
                selected_sub = filter(lambda x: x["title"] == attrib, selected)
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
            mid = submenu["id"]
            cq = [item for item in menu[mid] if item.has_key("clearquery")]
            for item in menu[mid]:
                cq = cq + [
                    subitem
                    for subitem in item["submenu"]
                    if subitem.has_key("clearquery")
                ]
            submenu["selected"] = cq

        return submenus

    def showSubmenu(self, submenu):
        """Returns True if submenu has an entry with query or clearquery set,
            i.e. should be displayed
        """
        return (
            not filter(lambda x: x.has_key("clearquery") or x["count"] > 0, submenu)
            == []
        )

    def expandSubmenu(self, submenu):
        """Returns True if submenu has an entry with clearquery set, i.e.
           should be displayed expanded
        """
        return (
            not filter(
                lambda x: x.has_key("clearquery") or self.expandSubmenu(x["submenu"]),
                submenu,
            )
            == []
        )
