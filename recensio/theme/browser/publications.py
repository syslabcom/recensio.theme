from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class PublicationsView(BrowserView):
    """ Overview page of publications """

    template = ViewPageTemplateFile('templates/publications.pt')

    def __call__(self):
        return self.template(self)

    def publications(self):
        pubs = [x for x in self.context.objectValues() if x.portal_type=="Publication"]
        return pubs
        
    def getimage(self, p):
        if 'logo' in p.objectIds():
            return p.absolute_url()+'/logo'
        return self.context.portal_url()+'/default_publication_logo.png'