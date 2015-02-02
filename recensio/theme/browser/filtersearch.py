from zope.app.component.hooks import getSite
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from Products.Five.browser import BrowserView
from Products.Archetypes.utils import DisplayList
from Products.ATContentTypes.interfaces import IATTopic

from plone.i18n.locales.languages import _languagelist

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
    show_if_empty = True

    def __init__(self, context, request):
        self.facet_fields = filter_facets
        self.default_query = {'portal_type': PORTAL_TYPES,
                              'facet': 'true',
                              'facet.field': self.facet_fields,
                              'b_size': 10,
                              'b_start': 0, }

        if IATTopic.providedBy(context):
            self.default_query.update(context.buildQuery())

        #self.vocDict = {'languageReview': listAvailableContentLanguages()}

        util = getUtility(
            IVocabularyFactory,
            u"recensio.policy.vocabularies.available_content_languages")
        vocab = util(getSite())
        terms = [(x.value, _languagelist[x.value][u'native'])
                 for x in vocab]
        self.vocDict = {'languageReview': DisplayList(terms)}

        self.submenus = [
            dict(title='Language',id='languageReview'),]

        self.queryparam = 'languageReview'

        BrowserView.__init__(self, context, request)

    def sort(self, submenu):
        return sorted(submenu, key=lambda x:x['name'])

