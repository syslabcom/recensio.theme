# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import normalizeString
from Products.Five.browser import BrowserView
from recensio.contenttypes import contenttypesMessageFactory as _
from recensio.contenttypes.config import REVIEW_TYPES
from zope.annotation.interfaces import IAnnotations
from ZTUtils import make_query


class ResultsListing(BrowserView):
    """Lists search results."""

    def normalizeString(self, text):
        return normalizeString(text)

    @property
    def portal_path(self):
        return api.portal.get().getPhysicalPath()


class ListingBase(BrowserView):
    """Base class for listing views."""

    show_language_filter = False

    @property
    def rss_url(self):
        return "{}/search_rss?{}".format(
            self.context.absolute_url(), make_query(self.query)
        )

    @property
    def items(self):
        catalog = api.portal.get_tool("portal_catalog")
        results = catalog(self.query)
        IAnnotations(self.request)["recensio.query_results"] = results
        return results

    def translate(self, msgid):
        translation_service = api.portal.get_tool('translation_service')
        return translation_service.utranslate(
            msgid=msgid,
            context=self.request,
        )

class ReviewSectionsListing(ListingBase):
    @property
    def title(self):
        return self.translate(_("label_latest_review_journals"))

    @property
    def query(self):
        navigation_root = getNavigationRoot(self.context)
        query = dict(
            portal_type=["Volume", "Issue"],
            path=navigation_root,
            fq="-hide_from_listing:true",
            sort_on="effective",
            sort_order="reverse",
        )
        return query


class ReviewItemsListing(ListingBase):
    show_language_filter = True

    @property
    def title(self):
        return self.translate(_("label_latest_reviews"))

    @property
    def query(self):
        navigation_root = getNavigationRoot(self.context)
        query = dict(
            portal_type=REVIEW_TYPES,
            path=navigation_root,
            facet_field=["languageReview"],
            sort_on="effective",
            sort_order="reverse",
        )
        if "languageReview" in self.request:
            query["languageReview"] = self.request.get("languageReview")
        return query
