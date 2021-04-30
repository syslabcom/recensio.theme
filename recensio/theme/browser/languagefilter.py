from plone.registry.interfaces import IRegistry
from Products.Archetypes.utils import DisplayList
from Products.Five.browser import BrowserView
from recensio.policy.interfaces import IRecensioSettings
from recensio.policy.utility import filter_facets
from topical import BrowseTopicsView
from zope.component import queryUtility


class LanguageFilterView(BrowseTopicsView):
    """Search view with language filter"""

    show_if_empty = True

    def __init__(self, context, request):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRecensioSettings)
        allowed_langs = (
            getattr(settings, "available_content_languages", "")
            .replace("\r", "")
            .split("\n")
        )
        self.vocDict = {"languageReview": DisplayList([(x, x) for x in allowed_langs])}

        self.submenus = [
            dict(title="Language", id="languageReview"),
        ]

        self.queryparam = "languageReview"

        BrowserView.__init__(self, context, request)

    @property
    def facet_fields(self):
        return filter_facets

    def sort(self, submenu):
        return sorted(submenu, key=lambda x: x["name"])
