from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from recensio.contenttypes.interfaces import IParentGetter


class HomepageView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/homepage.pt')

    def __call__(self):
        return self.template(self)

    def getReviewMonographs(self):
        pc = getToolByName(self.context, 'portal_catalog')
        plt = getToolByName(self.context, 'portal_languages')
        langinfo = plt.getAvailableLanguageInformation()
        query = dict(portal_type=["Review Monograph"],
            review_state="published",
            sort_on='effective',
            sort_order='reverse')
        resultset = list()
        for lang in ('en', 'de', 'fr'):
            q = query.copy()
            q['languageReview'] = [lang]
            res = pc(q)
            resultset.append(dict(language=lang,
                langname=langinfo[lang]['native'],
                results=res[:1]))
            # print "getReviewMonographs", lang, len(res)
        return resultset

    def getPrintedPresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Presentation Article Review',
                'Presentation Monograph', 'Presentation Collection'],
                review_state="published",
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        # print "getPrintedPresentations", len(res)
        return res[:3]

    def getOnlinePresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Presentation Online Resource'],
            review_state="published",
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        # print "getOnlinePresentations", len(res)
        return res[:3]

    def getReviewJournals(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Issue'],
            review_state="published",
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        resultset = list()
        for r in res[:3]:
            try:
                o = r.getObject()
            except:
                # XXX log error here
                continue
            pg = IParentGetter(o)
            publication = pg.get_parent_object_of_type('Publication')
            publication_title = publication and publication.Title() or u''
            publication_url = publication and publication.absolute_url() or u''
            volume = pg.get_parent_object_of_type('Volume')
            volume_title = volume and volume.Title() or u''
            volume_url = volume and volume.absolute_url() or u''
            # temporary hack until Issues can be added directly to publications
            # see #2458
            if volume_title == r.Title:
                volume_title = u''
            resultset.append(dict(Title=r.Title, review_url=r.getURL(),
                publication_title=publication_title,
                publication_url=publication_url,
                volume_title=volume_title,
                volume_url=volume_url,
                ))
        # print "getReviewJournals", len(res)
        return resultset
        
    def getPublications(self):
        portal = self.context.portal_url.getPortalObject()
        rezensionen = getattr(portal, 'rezensionen', None)
        zeitschriften = getattr(rezensionen, 'zeitschriften', None)
        pc = getToolByName(self.context, 'portal_catalog')
        if zeitschriften:
            query = dict(portal_type=['Publication'],
                review_state="published",
                path='/'.join(zeitschriften.getPhysicalPath()),
                sort_on='effective',
                sort_order='reverse')
            pubs = pc(query)
            return pubs
        else:
            # This can only happen, when there is no initial content yet
            return []
        
