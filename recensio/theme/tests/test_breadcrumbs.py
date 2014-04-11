import unittest2 as unittest
from plone.app.testing.helpers import login
from plone.app.testing.interfaces import SITE_OWNER_NAME
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

from recensio.policy.tests.layer import RECENSIO_INTEGRATION_TESTING
from recensio.theme.interfaces import IRecensioLayer


class TestBreadcrumbs(unittest.TestCase):
    layer = RECENSIO_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        alsoProvides(self.portal.REQUEST, IRecensioLayer)

    @unittest.skip("AttributeError: portal_membership - getMultiAdapter does"
                   "not return RootPhysicalNavigationBreadcrumbs on the"
                   "navigation root")
    def test_breadcrumbs_for_published_publication(self):
        login(self.layer['app'], SITE_OWNER_NAME)
        pub = self.portal.unrestrictedTraverse(
            '/plone/rezensionen/zeitschriften/francia-recensio')
        newid = pub.invokeFactory('Volume', id='test-volume')
        test_volume = pub.get(newid)
        newid = test_volume.invokeFactory('Issue', id='test-issue')
        test_issue = test_volume.get(newid)
        newid = test_issue.invokeFactory('Review Monograph', id='test-review')
        test_review = test_issue.get(newid)
        breadcrumbs_view = getMultiAdapter((test_review, self.portal.REQUEST),
                                           name='breadcrumbs_view')
        crumbs = breadcrumbs_view.breadcrumbs()
        self.assertEqual(len(crumbs), 7)

