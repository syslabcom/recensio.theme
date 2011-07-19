from plone.app.layout.sitemap.sitemap import SiteMapView
from Products.CMFCore.utils import getToolByName

class RecensioSiteMapView(SiteMapView):
    """ Customised sitemap which give reviews from Francia and
    Sehepunkte a low priority #3100 """

    def objects(self):
        """ Overrides the SiteMapView method """
        catalog = getToolByName(self.context, 'portal_catalog')
        for item in catalog.searchResults({'Language': 'all'}):
            location = item.getURL()
            map_item = {
                'loc'      : location,
                'lastmod'  : item.modified.ISO8601(),
                }
            if ("rezensionen/zeitschriften/francia-recensio" in location
                or "rezensionen/zeitschriften/sehepunkte" in location) \
                and item.portal_type in ["Review Monograph",
                                         "Review Journal"]:
                map_item['priority'] = 0.1
            yield map_item
