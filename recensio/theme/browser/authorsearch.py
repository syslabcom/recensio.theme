#!/usr/bin/python
# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.memoize import ram
from DateTime import DateTime

PRESENTATION_TYPES = ['Presentation Monograph',
                      'Presentation Online Resource',
                      'Presentation Article Review',
                      'Presentation Collection']
REVIEW_TYPES = ['Review Journal', 'Review Monograph']


class AuthorSearchView(BrowserView):

    ''' Dynamic elements on the homepage '''

    template = ViewPageTemplateFile('templates/authorsearch.pt')
    ALPHABET = [
        'A',
        'B',
        'C',
        'D',
        'E',
        'F',
        'G',
        'H',
        'I',
        'J',
        'K',
        'L',
        'M',
        'N',
        'O',
        'P',
        'Q',
        'R',
        'S',
        'T',
        'U',
        'V',
        'W',
        'X',
        'Y',
        'Z',
        ]

    def __call__(self):
        self.request.set('disable_border', True)
        return self.template(self)

    def _render_cachekey(method, self):
        current_date = DateTime().Date()
        return (current_date, )

    @ram.cache(_render_cachekey)
    def all_authors(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        reviews = catalog({
            'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"' \
                    % x, REVIEW_TYPES)) + ')',
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
            }).facet_counts['facet_fields']['authors']
        presentations = catalog({
            'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"' \
                    % x, PRESENTATION_TYPES)) + ')',
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
            }).facet_counts['facet_fields']['authors']
        comments = catalog({
            'fq': '+portal_type:"Discussion Item"',
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
            }).facet_counts['facet_fields']['authors']

        authors = self.request.get('authors')
        if authors:
            items = [x.lower() for x in authors.split(' ')]
            authors = [dict(name=x,
                       reviews=reviews.get(safe_unicode(x), 0),
                       presentations=presentations.get(safe_unicode(x),
                       0), comments=comments.get(safe_unicode(x), 0))
                       for x in catalog.uniqueValuesFor('authors')
                       if True in [y in x.lower() for y in items]]
        else:
            authors = [dict(name=x,
                       reviews=reviews.get(safe_unicode(x), 0),
                       presentations=presentations.get(safe_unicode(x),
                       0), comments=comments.get(safe_unicode(x), 0))
                       for x in catalog.uniqueValuesFor('authors')]
        authors = filter(lambda x: x['presentations'] + x['reviews'] \
                         + x['comments'] != 0, authors)

        return authors

    @property
    def authors(self):
        author_string = self.request.get('authors')
        if author_string:
            authors = [x.lower() for x in author_string.split(' ')]
            for one_author_data in self.all_authors():
                one_author_lowered = one_author_data['name'].lower()
                for author_searched in authors:
                    if author_searched in one_author_lowered():
                        yield one_author_data
        else:
            for one_author in self.all_authors():
                yield one_author

    @property
    @ram.cache(_render_cachekey)
    def alpha_index(self):
        alpha_index = {}
        for letter in self.ALPHABET:
            part = filter(lambda a: a['name'].startswith(letter),
                          self.authors)
            if part:
                alpha_index[letter] = self.authors.index(part[0])
        return alpha_index
