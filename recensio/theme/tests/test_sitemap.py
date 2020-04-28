# -*- coding: utf-8 -*-
import unittest2 as unittest
from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.interfaces import IRecensioLayer
from zope.component import getMultiAdapter
from zope.interface import alsoProvides


class TestSiteMap(unittest.TestCase):
    layer = RECENSIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        # Even though the layer is registered we still need to mark
        # the request with it so that layer specific views can be
        # accessed
        alsoProvides(self.portal.REQUEST, IRecensioLayer)

    def test_sitemap_priorities(self):
        """ The search engine sitemap has been customised to give a
        low priority to reviews from Sehepunkte or Francia #3100"""
        sitemap_view = getMultiAdapter(
            (self.portal, self.portal.REQUEST), name="sitemap.xml.gz"
        )

        obs_list = [i for i in sitemap_view.objects()]
        low_prio_obs = [
            i
            for i in obs_list
            if "zeitschriften/sehepunkte/vol1/issue1/" in i["loc"]
            or "zeitschriften/francia-recensio/vol1/issue1/" in i["loc"]
        ]
        unprioritised_obs = [
            i
            for i in obs_list
            if "zeitschriften/sehepunkte/vol1/issue1/" not in i["loc"]
            and "zeitschriften/francia-recensio/vol1/issue1/" not in i["loc"]
        ]

        low_prio_priorities = set([i["priority"] for i in low_prio_obs])
        high_prio_priorities = set([i.get("priority", None) for i in unprioritised_obs])

        self.assertEquals(
            low_prio_priorities,
            set([0.10000000000000001]),
            msg=u"All low priority items have a priority of 0.1",
        )
        self.assertEquals(
            high_prio_priorities,
            set([None]),
            msg=(
                u"Items which do not have a low priority do not have "
                "a priority specified"
            ),
        )
