# -*- coding: utf-8 -*-
import unittest2 as unittest
from plone.registry.interfaces import IRegistry
from recensio.policy.interfaces import IRecensioSettings
from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.browser.views import listAvailableContentLanguages
from zope.component import queryUtility


class TestLanguages(unittest.TestCase):
    layer = RECENSIO_INTEGRATION_TESTING

    def test_empty(self):
        langs = listAvailableContentLanguages()
        self.assertEqual(len(langs), 0)

    def test_valid_entries(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRecensioSettings)
        settings.available_content_languages = u'de\nen'
        langs = listAvailableContentLanguages()
        self.assertEqual(len(langs), 2)
        self.assertEqual(langs.items()[0], ('de', u'Deutsch'))
        self.assertEqual(langs.items()[1], ('en', u'English'))

    def test_invalid_entries(self):
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IRecensioSettings)
        settings.available_content_languages = u'de\nidontexist'
        self.assertRaises(KeyError, listAvailableContentLanguages)
