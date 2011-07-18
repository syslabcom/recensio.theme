# -*- coding: utf-8 -*-
import unittest2 as unittest

from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING

class TestSiteMap(unittest.TestCase):
    """
    """
    layer = RECENSIO_INTEGRATION_TESTING

    def test_priorities_sitemap(self):
        """ The search engine sitemap has been customised to give a
        low priority to reviews from Sehepunkte or Francia #3100"""
        pass
