from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class PublicationsView(BrowserView):
    """ Overview page of publications """

    template = ViewPageTemplateFile('templates/publications.pt')

    def __call__(self):
        return self.template(self)

    def publications(self):
        pc = self.context.portal_catalog
        publist = []
        currlang = self.context.portal_languages.getPreferredLanguage()
        pubs = pc(portal_type="Publication", 
                  path='/'.join(self.context.getPhysicalPath()), 
                  review_state='published')
        for pub in pubs:
            pubob = pub.getObject()
            if 'logo' in pubob.objectIds():
                logourl = pub.getURL()+'/logo/image_thumb'
            else:
                logourl = self.context.portal_url()+'/empty_publication.jpg'    
            defob = getattr(pubob, pubob.getDefaultPage()).getTranslation(currlang)
            title = defob.Title() != '' and defob.Title() \
                    or pubob.Title()
            desc = defob.Description()
            morelink = pubob.absolute_url()
            publist.append(dict(ob=pubob, title=title, desc=desc, logo=logourl, link=morelink))
        return publist
        
