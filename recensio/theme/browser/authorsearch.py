#!/usr/bin/python
# -*- coding: utf-8 -*-

from plone.memoize import instance
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from recensio.theme.browser.views import CrossPlatformMixin


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

    def get_b_start(self):
        b_start = int(self.request.get("b_start", 0))
        if b_start:
            return b_start
        else:
            letter = self.request.get("letter")
            if not letter:
                return 0
            letter = letter.lower()
            catalog = getToolByName(self.context, "portal_catalog")
            query = {
                "portal_type": "Person",
                "b_start": 0,
                "b_size": 0,
                "sort_on": "sortable_title",
                "fl": "Title",
            }
            num_authors = len(catalog(query))
            b_size = 2000
            b_start = num_authors / 2 - b_size / 2
            while True:
                query.update({
                    "b_start": b_start,
                    "b_size": b_size,
                })
                partition = catalog(query)
                last_index = min(b_start + b_size - 1, num_authors - 1)
                if partition[last_index]["Title"][0].lower() < letter:
                    b_start = min(b_start + (num_authors - b_start) / 2, num_authors)
                elif partition[b_start]["Title"][0].lower() > letter:
                    b_start = max(b_start - (num_authors - b_start) / 2, 0)
                else:
                    break
            for idx in range(b_start, last_index):
                if partition[idx]["Title"].lower().startswith(letter):
                    b_start = idx
                    break
        return b_start

    @property
    @instance.memoize
    def authors(self):
        catalog = getToolByName(self.context, "portal_catalog")
        author_string = safe_unicode(self.request.get("authors"))
        b_start = self.get_b_start()
        b_size = int(self.request.get("b_size", 30))
        query = {
            "portal_type": "Person",
            "b_start": b_start,
            "b_size": b_size,
            "sort_on": "sortable_title",
            "fl": "Title,UID,path_string",
        }
        if author_string:
            query["SearchableText"] = author_string.strip("\"'")
        return catalog(query)

    @property
    def portal_title(self):
        return getToolByName(self.context, "portal_url").getPortalObject().Title()
