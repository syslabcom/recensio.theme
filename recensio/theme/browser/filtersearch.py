from zope.component import queryUtility
from Products.Five.browser import BrowserView
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.interfaces import IATTopic

from plone.registry.interfaces import IRegistry

from recensio.policy.utility import filter_facets
from recensio.policy.interfaces import IRecensioSettings
from recensio.theme.browser.views import listAvailableContentLanguages
from topical import BrowseTopicsView

PORTAL_TYPES = ['Presentation Online Resource', 'Presentation Article Review',
    'Presentation Collection', 'Presentation Monograph',
        'Review Journal', 'Review Monograph' ]

class FilterSearchView(BrowseTopicsView):
    """Search view with language filter
    """

    def __init__(self, context, request):
        self.facet_fields = filter_facets
        self.default_query = {'portal_type': PORTAL_TYPES,
                              'facet': 'true',
                              'facet.field': self.facet_fields, }

        if IATTopic.providedBy(context):
            self.default_query.update(context.buildQuery())

        #self.vocDict = {'languageReview': listAvailableContentLanguages()}
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRecensioSettings)
        allowed_langs = getattr(settings, 'available_content_languages', '').replace('\r', '').split('\n')
        self.vocDict = {'languageReview': DisplayList([(x, x) for x in allowed_langs])}

        self.submenus = [
            dict(title='Language',id='languageReview'),]

        self.queryparam = 'languageReview'

        BrowserView.__init__(self, context, request)

    def sort(self, submenu):
        return sorted(submenu, key=lambda x:x['name'])

