from plone.app.layout.sitemap.sitemap import SiteMapView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import getNavigationRoot
from recensio.contenttypes.config import REVIEW_TYPES


class RecensioSiteMapView(SiteMapView):
    """Customised sitemap which give reviews from Francia and
    Sehepunkte a low priority #3100"""

    def objects(self):
        """Overrides the SiteMapView method"""
        catalog = getToolByName(self.context, "portal_catalog")
        root = getNavigationRoot(self.context)
        query = {
            "Language": "all",
            "path": root,
            "b_size": 10000,
        }
        results = catalog.searchResults(query)
        if None in results:
            query["b_size"] = len(results)
            results = catalog.searchResults(query)

        for item in results:
            location = item.getURL()
            map_item = {
                "loc": location,
                "lastmod": item.modified.ISO8601(),
            }
            if (
                "rezensionen/zeitschriften/francia-recensio" in location
                or "rezensionen/zeitschriften/sehepunkte" in location
            ) and item.portal_type in REVIEW_TYPES:
                map_item["priority"] = 0.1
            yield map_item
