#!/usr/bin/python
# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from DateTime import DateTime
from icu import Collator
from icu import Locale
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.memoize import instance
from plone.memoize import ram
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from recensio.contenttypes.config import PRESENTATION_TYPES
from recensio.contenttypes.config import REVIEW_TYPES
from recensio.theme.browser.views import CrossPlatformMixin
from zope.component import queryUtility


class AuthorSearchView(BrowserView, CrossPlatformMixin):

    """Dynamic elements on the homepage"""

    template = ViewPageTemplateFile("templates/authorsearch.pt")
    ALPHABET = [
        "A",
        "B",
        "C",
        "D",
        "E",
        "F",
        "G",
        "H",
        "I",
        "J",
        "K",
        "L",
        "M",
        "N",
        "O",
        "P",
        "Q",
        "R",
        "S",
        "T",
        "U",
        "V",
        "W",
        "X",
        "Y",
        "Z",
    ]

    def __call__(self):
        self.request.set("disable_border", True)
        return self.template(self)

    def _render_cachekey(method, self):
        current_date = DateTime().Date()
        navigation_root = getNavigationRoot(self.context)
        use_navigation_root = self.request.get("use_navigation_root", True)
        return (
            current_date,
            navigation_root,
            use_navigation_root,
        )

    @ram.cache(_render_cachekey)
    def all_authors(self):
        catalog = getToolByName(self.context, "portal_catalog")
        membership_tool = getToolByName(self.context, "portal_membership")
        portal_url = getToolByName(self.context, "portal_url")
        navigation_root = getNavigationRoot(self.context)

        base_query = {
            "facet": "true",
            "facet.field": "authorsUID",
            "facet.limit": "-1",
            "facet.mincount": "1",
            "b_size": 0,
        }
        state_query = "+review_state:published "
        if self.request.get("use_navigation_root", True):
            base_query["path"] = navigation_root

        review_query = base_query.copy()
        review_query.update(
            {
                "fq": state_query
                + "+portal_type:("
                + " OR ".join(map(lambda x: '"%s"' % x, REVIEW_TYPES))
                + ")",
            }
        )
        reviews = catalog(review_query).facet_counts["facet_fields"]["authorsUID"]

        presentation_query = base_query.copy()
        presentation_query.update(
            {
                "fq": state_query
                + "+portal_type:("
                + " OR ".join(map(lambda x: '"%s"' % x, PRESENTATION_TYPES))
                + ")",
            }
        )
        presentations = catalog(presentation_query).facet_counts["facet_fields"][
            "authorsUID"
        ]

        author_uids = set(presentations.keys() + reviews.keys())
        gnd_view = api.content.get_view(
            context=self.context, request=self.request, name="gnd-view"
        )

        def _get_name(uid):
            brain = gnd_view.getByUID(uid)
            return brain.Title if brain else ""

        pairs = [(uid, _get_name(uid)) for uid in author_uids]
        collator = Collator.createInstance(Locale("de_DE.UTF-8"))
        authors = [
            dict(
                uid=uid,
                name=name,
                display_name=name.strip(", "),
                reviews=reviews.get(uid, 0),
                presentations=presentations.get(uid, 0),
            )
            for uid, name in sorted(
                pairs,
                key=lambda author: collator.getSortKey(safe_unicode(author[1]).strip(
                    u", "
                )),
            )
        ]
        authors = filter(
            lambda x: x["presentations"] + x["reviews"] != 0,
            authors,
        )

        return authors

    @property
    @instance.memoize
    def authors(self):
        author_string = safe_unicode(self.request.get("authors"))
        if author_string:
            retval = []
            authors = [x.lower() for x in author_string.strip("\"'").split(" ")]
            for one_author_data in self.all_authors():
                one_author_lowered = one_author_data["name"].lower()
                all_tokens_found = True
                for author_searched in authors:
                    if author_searched not in one_author_lowered:
                        all_tokens_found = False
                        break
                if all_tokens_found:
                    retval.append(one_author_data)
            return retval
        else:
            return self.all_authors()

    @property
    def alpha_index(self):
        alpha_index = {}
        authors = self.authors
        for letter in self.ALPHABET:
            part = filter(lambda a: a["name"].startswith(letter), authors)
            if part:
                alpha_index[letter] = authors.index(part[0])
        return alpha_index

    @property
    def portal_title(self):
        return getToolByName(self.context, "portal_url").getPortalObject().Title()
