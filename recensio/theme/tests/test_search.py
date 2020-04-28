# -*- coding: utf-8 -*-
import unittest2 as unittest
from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.browser.views import RecensioHelperView
from recensio.theme.interfaces import IRecensioLayer
from zope.interface import alsoProvides
from zope.interface import noLongerProvides


class TestSearch(unittest.TestCase):
    """ """

    layer = RECENSIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.cat = self.portal.restrictedTraverse("queryCatalog")

    def assertOneSearchResult(self, search_text):
        res = self.cat(dict(SearchableText=search_text))
        self.assertEqual(
            len(res),
            1,
            msg="Did not get exactly one search result for {0}".format(search_text),
        )

    def test_find_isbn_in_full_text_search(self):
        alsoProvides(self.portal.REQUEST, IRecensioLayer)
        self.assertOneSearchResult("978-83-60448-41-7")
        self.assertOneSearchResult("9788360448417")
        self.assertOneSearchResult("978 83 60448 41 7")
        self.assertOneSearchResult("9-788-3604-48-41-7")
        self.assertOneSearchResult(u"9-788-3604-48-41-7 Černivci".encode("utf-8"))
        noLongerProvides(self.portal.REQUEST, IRecensioLayer)

    def test_normalize_isbns_in_text(self):
        helper_view = RecensioHelperView(self.portal, self.portal.REQUEST)
        res = helper_view.normalize_isbns_in_text("Niemcy 978-83-60448-39-7")
        self.assertEqual(res, "Niemcy 9788360448397")
        res = helper_view.normalize_isbns_in_text("Niemcy 978 83 60448 39 7")
        self.assertEqual(res, "Niemcy 9788360448397")

    def test_normalize_isbns_in_text_unicode(self):
        helper_view = RecensioHelperView(self.portal, self.portal.REQUEST)
        res = helper_view.normalize_isbns_in_text(
            u"społeczeństwa 978-83-60448-39-7".encode("utf-8")
        )
        self.assertEqual(res, u"społeczeństwa 9788360448397".encode("utf-8"))
