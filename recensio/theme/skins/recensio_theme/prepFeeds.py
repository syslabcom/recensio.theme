## Script (Python) "prepFeeds.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Prepare RSS Feeds
##


portalPath = context.portal_url.getPortalPath()
portalTitle = context.restrictedTraverse('plone_portal_state').portal_title()
#zss = context.rezensionen.zeitschriften.objectValues()
zss = context.portal_catalog(
  path=portalPath + '/rezensionen/zeitschriften',
  portal_type='Publication',
  sort_on='id',
)
feeds = []
parms = {}

tmpl = """../search_rss?modified_usage=range%%3Amin&isbn=&series=&sort_order=descending&year=&path:list=%(path)s&sort_on=created&titleOrShortname=&publisher=&created:date:list=1970/02/01&b_size:int=100&Creator=&modified:date:list=1970/02/01&submit=Suche&SearchableText=&place=&authorsFulltext=&created_usage=range%%3Amin&recensio_id=&rss_title=%(rss_title)s"""
#tmpl = """search_rss?rss_title=%(rss_title)s&modified_usage=range%%3Amin&sort_order=descending&path:list=%(path)s&sort_on=created&created:date:list=1970/02/01&b_size:int=100&modified:date:list=1970/02/01&submit=Suche&created_usage=range%%3Amin"""

for z in zss:
#  parms['path'] = '/'+z.absolute_url(1)
#  parms['path'] = '/'.join(z.getPhysicalPath())
  parms['path'] = z.getPath()
  parms['rss_title'] = '{0}: {1}'.format(portalTitle, z['Title'])
  zurl = tmpl % parms
  feeds.append((z['Title'], zurl))

return feeds

