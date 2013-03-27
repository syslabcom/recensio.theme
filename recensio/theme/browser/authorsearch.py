#!/usr/bin/python
# -*- coding: utf-8 -*-

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone.memoize import ram, instance
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
        membership_tool = getToolByName(self.context, 'portal_membership')

        reviews = catalog({
            'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"'
                    % x, REVIEW_TYPES)) + ')',
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
        }).facet_counts['facet_fields']['authors']
        presentations = catalog({
            'fq': '+portal_type:(' + ' OR '.join(map(lambda x: '"%s"'
                    % x, PRESENTATION_TYPES)) + ')',
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
        }).facet_counts['facet_fields']['authors']
        commentator_user_ids = catalog.uniqueValuesFor('commentators')
        comments = {}
        for commentator_id in commentator_user_ids:
            member = membership_tool.getMemberById(commentator_id)
            comments[safe_unicode(('%s, %s' % (
                member.getProperty('lastname'),
                member.getProperty('firstname'))
            )).encode('utf-8')] = 1

        authors = [dict(name=x.strip(', '),
                   reviews=reviews.get(safe_unicode(x), 0),
                   presentations=presentations.get(safe_unicode(x),
                   0), comments=comments.get(safe_unicode(x), 0))
                   for x in catalog.uniqueValuesFor('authors')]
        authors = filter(lambda x: x['presentations'] + x['reviews']
                         + x['comments'] != 0, authors)

        return authors

    @property
    @instance.memoize
    def authors(self):
        author_string = self.request.get('authors')
        if author_string:
            retval = []
            authors = [x.lower() for x in author_string.split(' ')]
            for one_author_data in self.all_authors():
                one_author_lowered = one_author_data['name'].lower()
                for author_searched in authors:
                    if author_searched in one_author_lowered:
                        retval.append(one_author_data)
                        break
            return retval
        else:
            return self.all_authors()

    @property
    def alpha_index(self):
        alpha_index = {}
        authors = self.authors
        for letter in self.ALPHABET:
            part = filter(lambda a: a['name'].startswith(letter),
                          authors)
            if part:
                alpha_index[letter] = authors.index(part[0])
        return alpha_index
