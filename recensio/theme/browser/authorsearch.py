#!/usr/bin/python
# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
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
        navigation_root = getNavigationRoot(self.context)
        use_navigation_root = self.request.get('use_navigation_root', True)
        return (current_date, navigation_root, use_navigation_root, )

    @ram.cache(_render_cachekey)
    def all_authors(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        membership_tool = getToolByName(self.context, 'portal_membership')
        portal_url = getToolByName(self.context, 'portal_url')
        navigation_root = getNavigationRoot(self.context)

        base_query = {
            'facet': 'true',
            'facet.field': 'authors',
            'facet.limit': '-1',
            'facet.mincount': '1',
        }
        state_query = '+review_state:published '
        if self.request.get('use_navigation_root', True):
            base_query['path'] = navigation_root

        review_query = base_query.copy()
        review_query.update({
            'fq': state_query + '+portal_type:(' + ' OR '.join(
                map(lambda x: '"%s"' % x, REVIEW_TYPES)) + ')',
        })
        reviews = catalog(review_query).facet_counts['facet_fields']['authors']

        presentation_query = base_query.copy()
        presentation_query.update({
            'fq': state_query + '+portal_type:(' + ' OR '.join(
                map(lambda x: '"%s"' % x, PRESENTATION_TYPES)) + ')',
        })
        presentations = catalog(presentation_query).facet_counts['facet_fields']['authors']

        comment_query = base_query.copy()
        comment_query.update({
            'fq': state_query + '+portal_type:(' + ' OR '.join(
                map(lambda x: '"%s"' % x, REVIEW_TYPES + PRESENTATION_TYPES)) + ')',
            'facet.field': 'commentators',
        })
        comments = catalog(comment_query).facet_counts['facet_fields']['commentators']
        commentator_user_ids = comments.keys()
        comments = {}
        for commentator_id in commentator_user_ids:
            member = membership_tool.getMemberById(commentator_id)
            if not member:
                portal = portal_url.getPortalObject()
                siblings = aq_parent(portal).objectValues('Plone Site')
                for sibling in siblings:
                    if sibling == portal:
                        continue
                    mt = getToolByName(sibling, 'portal_membership')
                    member = mt.getMemberById(commentator_id)
                    if member:
                        break
                if not member:
                    continue
            comments[safe_unicode(('%s, %s' % (
                member.getProperty('lastname'),
                member.getProperty('firstname'))
            ))] = commentator_id

        author_names = set(
            presentations.keys() + reviews.keys() + comments.keys())
        authors = [dict(name=x.strip(', '),
                   reviews=reviews.get(safe_unicode(x), 0),
                   presentations=presentations.get(safe_unicode(x),
                   0), comments=comments.get(safe_unicode(x), 0))
                   for x in sorted(author_names)]
        authors = filter(lambda x: x['presentations'] + x['reviews']
                         + (1 if x['comments'] else 0) != 0, authors)

        return authors

    @property
    @instance.memoize
    def authors(self):
        author_string = self.request.get('authors')
        if author_string:
            retval = []
            authors = [x.lower() for x in author_string.strip("\"'").split(' ')]
            for one_author_data in self.all_authors():
                one_author_lowered = one_author_data['name'].lower()
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
            part = filter(lambda a: a['name'].startswith(letter),
                          authors)
            if part:
                alpha_index[letter] = authors.index(part[0])
        return alpha_index

    @property
    def portal_title(self):
        return getToolByName(self.context, 'portal_url').getPortalObject().Title()
