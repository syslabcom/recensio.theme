from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class HomepageView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/homepage.pt')

    def __call__(self):
        return self.template(self)

    def getReviewMonographs(self):
        pc = getToolByName(self.context, 'portal_catalog')
        plt = getToolByName(self.context, 'portal_languages')
        langinfo = plt.getAvailableLanguageInformation()
        # import pdb; pdb.set_trace()
        query = dict(portal_type="Review Monograph",
            Language='all',
            sort_on='effective',
            sort_order='reverse')
        resultset = list()
        for lang in ('en', 'de', 'fr'):
            q = query.copy()
            q['languageReview'] = lang
            res = pc(q)
            resultset.append(dict(language=lang,
                langname=langinfo[lang]['native'],
                results=res[:5]))

        return resultset

    def getPrintedPresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=('Presentation Article Review',
                'Presentation Monograph', 'Presentation Collection'),
            Language='all',
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        return res[:5]

    def getOnlinePresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type='Presentation Online Resource',
            Language='all',
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        return res[:5]

    def getReviewJournals(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type='Review Journal',
            Language='all',
            sort_on='effective',
            sort_order='reverse')
        res = pc(query)
        resultset = list()
        for r in res[:5]:
            try:
                o = r.getObject()
            except:
                # XXX log error here
                continue
            publication = o.get_publication_object()
            publication_title = publication and publication.Title() or u''
            publication_url = publication and publication.absolute_url() or u''
            resultset.append(dict(Title=r.Title, review_url=r.getURL(),
                publication_title=publication_title,
                publication_url=publication_url,
                ))
        return resultset
