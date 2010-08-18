from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class AuthorSearchView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/authorsearch.pt')

    def __call__(self):
        return self.template(self)

    @property
    def authors(self):
        if not hasattr(self, '_authors'):
            catalog = getToolByName(self.context, 'portal_catalog')
            authors = self.request.get('authors')
            if authors:
                self._authors = [x for x in catalog.uniqueValuesFor('authors') if True in [y in x for y in authors.split(' ')]]
            else:
                self._authors = catalog.uniqueValuesFor('authors')
        return self._authors
