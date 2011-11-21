from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from recensio.contenttypes.interfaces import IParentGetter
from plone.i18n.locales.languages import _languagelist
from ZTUtils import make_query

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

REVIEW_LANGUAGES = [u'en', u'de', u'']

class HomepageView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/homepage.pt')
    
    def _render_cachekey(method, self):
        preflang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
        return (preflang)
        
    @ram.cache(_render_cachekey)
    def __call__(self):
        return xhtml_compress(self.template(self))

    def format_effective_date(self, date_string):
        """Format the publication date as specified in #2627"""
        if date_string == 'None':
            return ''
        date = DateTime(date_string)
        return "%s-%02d-%02d" % (date.year(), date.month(), date.day())

    def format_authors(self, brain):
        ob = brain.getObject()
        authors = getattr(ob, "authors", "")
        if len(authors) > 0:
            firstname = authors[0]["firstname"].strip()
            initial = len(firstname) > 0 and firstname[0]+". " or ""
            lastname = authors[0]["lastname"]
            et_al = len(authors) > 1 and " et al." or ""
            if len(lastname) > 0:
                return "%s%s%s:" %(initial, lastname, et_al)
        return ""

    def getReviewMonographs(self):
        pc = getToolByName(self.context, 'portal_catalog')
        langinfo = _languagelist.copy()
        langinfo[''] = { 'name':   'International',
                         'native': 'int'}
        query = dict(portal_type=["Review Monograph", "Review Journal"],
            review_state="published",
            sort_on='effective',
            sort_order='reverse')
        resultset = list()
        for lang in REVIEW_LANGUAGES:
            q = query.copy()
            if lang:
                q['languageReview'] = [lang]
            else:
                q['languageReview'] = list(
                    set(langinfo.keys()).difference(set(REVIEW_LANGUAGES)))
            res = pc(q)
            resultset.append(
                dict(
                    language=lang or 'int',
                    langname=langinfo[lang]['native'],
                    results=res[:5],
                    query_str=make_query(q))
                )
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
            resultset.append(
                dict(
                    Title=r.Title,
                    effective_date=self.format_effective_date(r.EffectiveDate),
                    publication_title=publication_title,
                    publication_url=publication_url,
                    review_url=r.getURL(),
                    volume_title=volume_title,
                    volume_url=volume_url,
                    review_brain=r
                    )
                )
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
                sort_on='Title')
            pubs = pc(query)
            return sorted(pubs, key=lambda p: p['Title'].lower())
        else:
            # This can only happen, when there is no initial content yet
            return []

