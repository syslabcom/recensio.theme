# -*- coding: utf-8 -*-
from plone import api
from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.interfaces import IRecensioLayer
from zope.interface import alsoProvides
from zope.interface import noLongerProvides
import unittest2 as unittest


class TestAuthorSearch(unittest.TestCase):
    """ """

    layer = RECENSIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"].clone()
        alsoProvides(self.request, IRecensioLayer)

    def tearDown(self):
        noLongerProvides(self.request, IRecensioLayer)

    def get_b_start(self):
        view = api.content.get_view(
            context=self.portal, request=self.request, name="authorsearch"
        )
        b_start = view.get_b_start()
        return b_start

    def test_alphabet_a(self):
        self.request.form = {"letter": "A"}
        b_start = self.get_b_start()
        self.assertEqual(b_start, 0)

    def test_alphabet_h(self):
        self.request.form = {"letter": "H"}
        b_start = self.get_b_start()
        self.assertEqual(b_start, 30)

    def test_alphabet_k(self):
        self.request.form = {"letter": "K"}
        b_start = self.get_b_start()
        self.assertEqual(b_start, 60)

    def test_alphabet_r(self):
        self.request.form = {"letter": "R"}
        b_start = self.get_b_start()
        self.assertEqual(b_start, 90)

    def test_alphabet_z(self):
        self.request.form = {"letter": "Z"}
        b_start = self.get_b_start()
        self.assertEqual(b_start, 120)

    def test_search(self):
        self.request.form = {"authors": "Eimer"}
        view = api.content.get_view(
            context=self.portal, request=self.request, name="authorsearch"
        )
        result = view.authors
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["Title"], "Eimer, Claudio")
        self.assertEqual(result[1]["Title"], "Eimer, Kathy")
