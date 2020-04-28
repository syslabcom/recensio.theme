## Script (Python) "solr_boost_index_values"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=data
##title=Calculate field and document boost values for Solr

# this script is meant to be customized according to site-specific
# search requirements, e.g. boosting certain content types like "news items",
# ranking older content lower, consider special important content items,
# content rating etc.
#
# the indexing data that will be sent to Solr is passed in as the `data`
# parameter, the indexable object is available via the `context` binding.
# the return value should be a dictionary consisting of field names and
# their respecitive boost values.  use an empty string as the key to set
# a boost value for the entire document/content item.
if context.portal_type in [
    "Review Monograph",
    "Review Journal",
    "Review Article Journal",
    "Review Article Collection",
    "Review Exhibition",
    "Presentation Monograph",
    "Presentation Article Review",
    "Presentation Collection",
    "Presentation Online Resource",
]:
    return {"": 256.0, "SearchableText": 256.0}
path = "/".join(context.getPhysicalPath())
path = path.replace("-fr", "").replace("-en", "")
if path.startswith("/recensio/newsletter/archiv"):
    return {"": 2.2250738585072014e-308, "SearchableText": 2.2250738585072014e-308}
else:
    return {}
