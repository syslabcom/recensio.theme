from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from recensio.contenttypes.interfaces import IParentGetter
from plone.i18n.locales.languages import _languagelist
from ZTUtils import make_query
from Acquisition import aq_inner
from zope.component import getMultiAdapter

from plone.memoize import ram
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

import logging
log = logging.getLogger('recensio.theme')

REVIEW_LANGUAGES = [u'en', u'de', u'']

class HomepageView(BrowserView):
    """ Dynamic elements on the homepage """

    template = ViewPageTemplateFile('templates/homepage.pt')

    def _render_cachekey(method, self):
        preflang = getToolByName(
            self.context, 'portal_languages').getPreferredLanguage()
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        roles = member.getRolesInContext(self.context)

        today = DateTime().strftime("%Y-%m-%d")
        return (preflang, roles, today)

#    @ram.cache(_render_cachekey)
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
        if len(authors) == 0 or authors == ({'lastname' : '', 'firstname' : ''},):
            authors = getattr(ob, "editorial", "")
        if len(authors) == 0:
            return ""
        firstname = authors[0]["firstname"].strip()
        initial = len(firstname) > 0 and safe_unicode(firstname)[0].encode('utf-8')+". " or ""
        lastname = authors[0]["lastname"]
        et_al = len(authors) > 1 and " et al." or ""
        if len(lastname) > 0:
            return "%s%s%s:" %(initial, lastname, et_al)
        return ""

    @ram.cache(_render_cachekey)
    def getReviewMonographs(self):
        pc = getToolByName(self.context, 'portal_catalog')
        langinfo = _languagelist.copy()
        langinfo[''] = { 'name':   'International',
                         'native': 'int'}
        query = dict(portal_type=["Review Monograph", "Review Journal"],
            review_state="published",
            sort_on='effective',
            sort_order='reverse', b_size=5)
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
                    results=[dict(authors=self.format_authors(x),
                                    url=x.getURL(),
                                    title=x.getObject().punctuated_title_and_subtitle,
                                    date=self.format_effective_date(x['EffectiveDate'])) for x in res[:5]],
                    query_str=make_query(q))
                )
            # print "getReviewMonographs", lang, len(res)
        return resultset

    @ram.cache(_render_cachekey)
    def getPrintedPresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Presentation Article Review',
                'Presentation Monograph', 'Presentation Collection'],
                review_state="published",
            sort_on='effective',
            sort_order='reverse', b_size=3)
        res = pc(query)
        data = []
        for r in res[:3]:
            ob = r.getObject()
            data.append(dict(url=r.getURL(),
                            authors=self.format_authors(r),
                            title=ob.punctuated_title_and_subtitle,
                            date=self.format_effective_date(r['EffectiveDate'])))
        return data

    @ram.cache(_render_cachekey)
    def getOnlinePresentations(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Presentation Online Resource'],
            review_state="published",
            sort_on='effective',
            sort_order='reverse', b_size=3)
        res = pc(query)
        # print "getOnlinePresentations", len(res)
        data = []
        for r in res[:3]:
            data.append(dict(url=r.getURL(), title=r['Title'], date=self.format_effective_date(r['EffectiveDate'])))
        return data

    @ram.cache(_render_cachekey)
    def getReviewJournals(self):
        pc = getToolByName(self.context, 'portal_catalog')
        query = dict(portal_type=['Issue', 'Volume'],
            review_state="published",
            sort_on='effective',
            sort_order='reverse', b_size=6)
        res = pc(query)[:6]
        resultset = list()
        objects = {}
        for r in res:
            objects[r.getObject()] = r
        for obj, brain in objects.items():
            if obj.portal_type == "Issue" and \
                obj.__parent__.portal_type == "Volume":
                if obj.__parent__ in objects.keys() \
                   and objects[obj.__parent__] in res:
                    res.remove(objects[obj.__parent__])
        for r in res:
            if not r:
                continue
            try:
                o = r.getObject()
            except AttributeError:
                log.exception("Could not get object. Probably this means "
                    "there is a mismatch with solr")
                continue
            if o not in objects:
                continue
            pg = IParentGetter(o)
            publication = pg.get_parent_object_of_type('Publication')
            publication_title = publication and publication.Title() or u''
            publication_url = publication and publication.absolute_url() or u''
            if o.portal_type == 'Volume':
                volume = o
            else:
                volume = pg.get_parent_object_of_type('Volume')
            volume_title = volume and volume.Title() or u''
            volume_url = volume and volume.absolute_url() or u''
            resultset.append(
                dict(
                    Title=r.Title,
                    effective_date=self.format_effective_date(r.EffectiveDate),
                    publication_title=publication_title,
                    publication_url=publication_url,
                    review_url=r.getURL(),
                    volume_title=volume_title,
                    volume_url=volume_url
                    )
                )
        # print "getReviewJournals", len(res)
        return resultset[:3]

    @ram.cache(_render_cachekey)
    def getPublications(self):
        portal = self.context.portal_url.getPortalObject()
        rezensionen = getattr(portal, 'rezensionen', None)
        zeitschriften = getattr(rezensionen, 'zeitschriften', None)
        pc = getToolByName(self.context, 'portal_catalog')
        if zeitschriften:
            query = dict(portal_type=['Publication'],
                review_state="published",
                path='/'.join(zeitschriften.getPhysicalPath()),
                sort_on='Title', b_size=1000)

            context = aq_inner(self.context)
            portal_state = getMultiAdapter(
                (context, self.request), name=u'plone_portal_state')

            lang = portal_state.language()
            pubs = [brain.getObject().restrictedTraverse(brain.getObject().getDefaultPage()).getTranslations()[lang][0] for brain in pc(query)]
            items = [dict(title=x.Title(), url='/'+x.absolute_url(1)) for x in pubs]
            return sorted(items, key=lambda p: p['title'].lower())
        else:
            # This can only happen, when there is no initial content yet
            return []

