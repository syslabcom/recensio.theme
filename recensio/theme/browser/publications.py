from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize


class PublicationsView(BrowserView):
    """ Overview page of publications """

    template = ViewPageTemplateFile('templates/publications.pt')

    def _render_cachekey(method, self):
        preflang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
        return (preflang)

    @ram.cache(_render_cachekey)
    def __call__(self):
        return xhtml_compress(self.template(self))

    def publications(self):
        pc = self.context.portal_catalog
        publist = []
        currlang = self.context.portal_languages.getPreferredLanguage()
        pubs = pc(portal_type="Publication", 
                  path='/'.join(self.context.getPhysicalPath()), 
		  sort_on="sortable_title",
                  review_state='published')
        for pub in pubs:
            pubob = pub.getObject()
            if 'logo' in pubob.objectIds():
                logourl = pub.getURL()+'/logo/image_thumb'
            else:
                logourl = self.context.portal_url()+'/empty_publication.jpg'
            if pubob.getDefaultPage():
                defob = getattr(pubob, pubob.getDefaultPage())
                defob = defob.getTranslation(currlang) or defob
            else:
                defob = pubob
            title = defob and defob.Title() != '' and defob.Title() \
                    or pubob.Title()
            desc = defob and defob.Description() or pubob.Description()
            morelink = defob and defob.absolute_url() or ""
            publist.append(dict(ob=pubob, title=title, desc=desc, logo=logourl, link=morelink))
        return publist
        
