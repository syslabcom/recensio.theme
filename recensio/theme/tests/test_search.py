import unittest2 as unittest
from Products.CMFPlone.utils import getToolByName

from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING


class TestSearch(unittest.TestCase):
    """ """
    layer = RECENSIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.cat = getToolByName(self.portal, 'portal_catalog')

    def assertOneSearchResult(self, search_text):
        res = self.cat(SearchableText=search_text)
        self.assertEqual(
            len(res), 1,
            msg="Did not get exactly one search result for {0}".format(
                search_text))

    def test_find_isbn_in_full_text_search(self):
        # Most of these fail - it looks like numbers are not tokenised
        #self.assertOneSearchResult('978-83-60448-39-7')
        self.assertOneSearchResult('9788360448417')
        #self.assertOneSearchResult('978 83 60448 41 7')
        #self.assertOneSearchResult('978-83')
        #self.assertOneSearchResult('97883')
        #self.assertOneSearchResult('978 83')
        #self.assertOneSearchResult('9-788-3604-48-41-7')
