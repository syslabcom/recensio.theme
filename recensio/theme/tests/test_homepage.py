import unittest2 as unittest
from plone import api
from plone.app.testing.helpers import login
from plone.app.testing.interfaces import SITE_OWNER_NAME
from plone.app.testing.interfaces import TEST_USER_NAME
from recensio.contenttypes.content.reviewjournal import ReviewJournal
from recensio.contenttypes.content.reviewmonograph import ReviewMonograph
from recensio.contenttypes.setuphandlers import add_number_of_each_review_type
from recensio.policy.tests.layer import RECENSIO_BARE_INTEGRATION_TESTING


class TestHomepage(unittest.TestCase):
    layer = RECENSIO_BARE_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        login(self.layer['app'], SITE_OWNER_NAME)
        for tab in ['autoren',
                    'faq',
                    'presse',
                    'themen-epochen-regionen',
                    'ueberuns',
                    ]:
            api.content.create(
                container=self.portal,
                type='Folder',
                id=tab,
            )
        add_number_of_each_review_type(
            self.portal, 1, rez_classes=[ReviewMonograph, ReviewJournal])

        self.sehepunkte = self.portal['rezensionen']['zeitschriften']['sehepunkte']
        api.content.transition(obj=self.sehepunkte, to_state='published')
        self.sehepunkte.reindexObject()

        view = api.content.get_view(context=self.sehepunkte,
                                    request=self.request,
                                    name='solr-maintenance')
        view.reindex()

        login(self.portal, TEST_USER_NAME)

    def test_homepage_does_not_break_if_default_page_missing(self):
        self.sehepunkte.setDefaultPage(None)
        front_page = self.portal['front-page']
        homepage = api.content.get_view(
            context=front_page, request=self.request, name='homepage-view')
        homepage.getPublications()

    def test_homepage_shows_existing_default_page(self):
        login(self.layer['app'], SITE_OWNER_NAME)
        default_page = api.content.create(
            container=self.sehepunkte,
            type='Document',
            id='index_html',
            Title='Sehepunkte',
        )
        default_page = self.sehepunkte['index_html']
        api.content.transition(obj=default_page, to_state='published')
        self.sehepunkte.setDefaultPage(default_page.getId())
        login(self.portal, TEST_USER_NAME)

        front_page = self.portal['front-page']
        homepage = api.content.get_view(
            context=front_page, request=self.request, name='homepage-view')
        publications = homepage.getPublications()
        self.assertIn(default_page.Title(), [p['title'] for p in publications])
