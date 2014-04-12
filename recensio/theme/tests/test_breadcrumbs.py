import unittest2 as unittest
from Products.CMFCore.utils import getToolByName
from plone.app.testing.helpers import login, logout
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

        login(self.layer['app'], SITE_OWNER_NAME)
        self.pub = self.portal.unrestrictedTraverse(
            '/plone/rezensionen/zeitschriften/francia-recensio')
        self.test_volume_id = self.pub.invokeFactory(
            'Volume', id='test-volume')
        self.test_volume = self.pub.get(self.test_volume_id)
        newid = self.test_volume.invokeFactory('Issue', id='test-issue')
        self.test_issue = self.test_volume.get(newid)
        newid = self.test_issue.invokeFactory(
            'Review Monograph', id='test-review')
        self.test_review = self.test_issue.get(newid)

        # why is RootPhysicalNavigationBreadcrumbs not registered? Doing it
        # manually here
        from plone.app.layout.navigation.interfaces import INavigationRoot
        from Products.CMFPlone.browser.navigation import RootPhysicalNavigationBreadcrumbs
        from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
        from zope.publisher.interfaces.http import IHTTPRequest
        sm = self.portal.getSiteManager()
        sm.registerAdapter(factory=RootPhysicalNavigationBreadcrumbs,
                           required=(INavigationRoot, IHTTPRequest),
                           name='breadcrumbs_view',
                           provided=INavigationBreadcrumbs)

    def tearDown(self):
        login(self.layer['app'], SITE_OWNER_NAME)
        self.pub.manage_delObjects([self.test_volume_id])

    def test_breadcrumbs_for_published_publication(self):
        breadcrumbs_view = getMultiAdapter(
            (self.test_review, self.portal.REQUEST),
            name='breadcrumbs_view')
        crumbs = breadcrumbs_view.breadcrumbs()
        #FIXME: /plone/rezensionen/zeitschriften provides IBrowserDefault
        # for some reason, so it is skipped in the breadcrumbs. Not
        # so in a regular site.
        urls = [cr['absolute_url'].replace(
            'rezensionen', 'rezensionen/zeitschriften') for cr in crumbs]
        self.assertEqual(len(crumbs), 5)
        self.assertIn(self.pub.absolute_url(), urls)
        self.assertIn(self.test_volume.absolute_url(), urls)
        self.assertIn(self.test_issue.absolute_url(), urls)

    def test_breadcrumbs_for_unpublished_publication(self):
        login(self.layer['app'], SITE_OWNER_NAME)
        wf_tool = getToolByName(self.portal, 'portal_workflow')
        wf_tool.doActionFor(self.pub, 'hide')
        logout()

        breadcrumbs_view = getMultiAdapter(
            (self.test_review, self.portal.REQUEST),
            name='breadcrumbs_view')
        crumbs = breadcrumbs_view.breadcrumbs()
        #FIXME: /plone/rezensionen/zeitschriften provides IBrowserDefault
        # for some reason, so it is skipped in the breadcrumbs. Not
        # so in a regular site.
        urls = [cr['absolute_url'].replace(
            '/rezensionen/', '/rezensionen/zeitschriften/') for cr in crumbs]
        self.assertEqual(len(crumbs), 5)
        self.assertNotIn(self.pub.absolute_url(), urls)
        self.assertNotIn(self.test_volume.absolute_url(), urls)
        self.assertNotIn(self.test_issue.absolute_url(), urls)

        login(self.layer['app'], SITE_OWNER_NAME)
        wf_tool.doActionFor(self.pub, 'show')
        logout()
