from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode

PRESENTATION_TYPES = ['Presentation Monograph', 'Presentation Online Resource', 'Presentation Article Review', 'Presentation Collection']
REVIEW_TYPES = ['Review Journal', 'Review Monograph']

class AuthorSearchView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/authorsearch.pt')
    ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    def __call__(self):
        self.request.set('disable_border', True)
        return self.template(self)

    @property
    def authors(self):
        if not hasattr(self, '_authors'):
            catalog = getToolByName(self.context, 'portal_catalog')
            reviews = catalog({'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"' % x, REVIEW_TYPES)) + ')',
                               'facet': 'true',
                               'facet.field': 'authors',
                               'facet.limit': '-1',
                               'facet.mincount': '1'}).facet_counts['facet_fields']['authors']
            presentations = catalog({'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"' % x, PRESENTATION_TYPES)) + ')',
                                     'facet': 'true',
                                     'facet.field': 'authors',
                                     'facet.limit': '-1',
                                     'facet.mincount': '1'}).facet_counts['facet_fields']['authors']
            comments = catalog({'fq': '+portal_type:"Discussion Item"',
                                'facet': 'true',
                                'facet.field': 'authors',
                                'facet.limit': '-1',
                                'facet.mincount': '1'}).facet_counts['facet_fields']['authors']

            authors = self.request.get('authors')
            if authors:
                items = [x.lower() for x in authors.split(' ')]
                self._authors = [dict(name=x, reviews=reviews.get(safe_unicode(x), 0), presentations=presentations.get(safe_unicode(x), 0), comments=comments.get(safe_unicode(x), 0)) for x in
                    catalog.uniqueValuesFor('authors') if True in
                    [y in x.lower() for y in items]]
            else:
                self._authors = [dict(name=x, reviews=reviews.get(safe_unicode(x), 0), presentations=presentations.get(safe_unicode(x), 0), comments=comments.get(safe_unicode(x), 0)) for x in
                    catalog.uniqueValuesFor('authors')]
            self._authors = filter(lambda x: x['presentations'] + x['reviews'] + x['comments'] != 0, self._authors)

            self._alpha_index = {}
            for letter in self.ALPHABET:
                part = filter(lambda a: a['name'].startswith(letter), self._authors)
                if part:
                    self._alpha_index[letter] = self._authors.index(part[0])
        return self._authors

    @property
    def alpha_index(self):
        authors = self.authors
        return self._alpha_index
