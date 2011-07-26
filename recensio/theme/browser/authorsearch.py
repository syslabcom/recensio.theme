from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

PRESENTATION_TYPES = ['Presentation Monograph', 'Presentation Online Resource', 'Presentation Article Review', 'Presentation Collection']
REVIEW_TYPES = ['Review Journal', 'Review Monograph']

class AuthorSearchView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/authorsearch.pt')

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
                self._authors = [dict(name=x, reviews=reviews.get(x.decode('utf-8'), 0), presentations=presentations.get(x.decode('utf-8'), 0), comments=comments.get(x.decode('utf-8'), 0)) for x in
                    catalog.uniqueValuesFor('authors') if True in
                    [y in x.lower() for y in items]]
            else:
                self._authors = [dict(name=x, reviews=reviews.get(x.decode('utf-8'), 0), presentations=presentations.get(x.decode('utf-8'), 0), comments=comments.get(x.decode('utf-8'), 0)) for x in
                    catalog.uniqueValuesFor('authors')]
        return self._authors
