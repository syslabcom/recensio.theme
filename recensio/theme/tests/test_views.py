# -*- coding: utf-8 -*-
import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry
from recensio.policy.interfaces import IRecensioSettings
from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.browser.views import listAvailableContentLanguages
from zope.component import queryUtility


class TestLanguages(unittest.TestCase):
    layer = RECENSIO_INTEGRATION_TESTING

    def test_default_values(self):
        langs = listAvailableContentLanguages()
        self.assertEqual(len(langs), 10)
        self.assertIn(u'italian', langs)
        self.assertEqual(langs.getValue(u'italian'), u'Italian')
        self.assertIn(u'french', langs)
        self.assertEqual(langs.getValue(u'french'), u'French')

    def test_translated_value(self):
        voctool = getToolByName(self.layer['portal'], 'portal_vocabularies')
        vocab = voctool.get('available_content_languages')
        vocab.addTranslation('de')
        italian_de = vocab.get('italian').addTranslation('de')
        italian_de.setTitle(u'Italienisch')

        langs = listAvailableContentLanguages()
        self.assertIn(u'italian', langs)
        self.assertEqual(langs.getValue(u'italian'), u'Italienisch')
