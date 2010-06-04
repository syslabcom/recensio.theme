import logging
#from zope import component
#from plone.portlets.interfaces import IPortletManager
#from plone.portlets.interfaces import IPortletAssignmentMapping
#from Products.CMFCore.utils import getToolByName

#from portlets import extranet_navigation


#TYPES_WITH_ICONS = {
#    'Blog Entry':   'string:${portal_url}/++resource++recensio.theme.images/article32.png',
#    'Blog':         'string:${portal_url}/++resource++recensio.theme.images/contactcard32.png',
#    'Document':     'string:${portal_url}/++resource++recensio.theme.images/linedpaper32.png',
#    'Event':        'string:${portal_url}/++resource++recensio.theme.images/notepencil32.png',
#    'News Item':    'string:${portal_url}/++resource++recensio.theme.images/article32.png',
#    'File':         'string:${portal_url}/++resource++recensio.theme.images/paperstar32.png',
#    'Folder':       'string:${portal_url}/++resource++recensio.theme.images/folder32.png',
#    'HelpCenter':   'string:${portal_url}/++resource++recensio.theme.images/shieldcross32.png',
#    'HelpCenterKnowledgeBase':
#                    'string:${portal_url}/++resource++recensio.theme.images/lightbulb32.png',
#    'Image':        'string:${portal_url}/++resource++recensio.theme.images/paperphoto32.png',
#    'Link':         'string:${portal_url}/++resource++recensio.theme.images/contactbook32.png',
#    'Internal Link':'string:${portal_url}/++resource++recensio.theme.images/linedpaperplus32.png',
#    'PlonePopoll':  'string:${portal_url}/++resource++recensio.theme.images/bargraph32.png',
#    'TaskRequest':  'string:${portal_url}/++resource++recensio.theme.images/notecheck32.png',
#    'Topic':        'string:${portal_url}/++resource++recensio.theme.images/paperheart32.png',
#    'Ploneboard':   'string:${portal_url}/++resource++recensio.theme.images/users32.png',
#    }

# 'Gallery':      'string:${portal_url}/++resource++recensio.theme.images/camera32.png',

log = logging.getLogger('recensio.theme.setuphandlers.py')

#def setupVarious(context):
#    """ Ordinarily, GenericSetup handlers check for the existence of XML files.
#        Here, we are not parsing an XML file, but we use this text file as a
#        flag to check that we actually meant for this import step to be run.
#        The file is found in profiles/default.
#    """
#    if context.readDataFile('recensio.theme_various.txt') is None:
#        return
#
#    portal = context.getSite()
#    if portal.hasObject('front-page'):
#        portal.manage_delObjects(['front-page'])


#def setTypeIcons(context):
#    """ """
#    if context.readDataFile('recensio.theme_various.txt') is None:
#        return
#
#    portal = context.getSite()
#    pt = getToolByName(portal, 'portal_types')
#    for type in TYPES_WITH_ICONS.keys():
#        info = pt.getTypeInfo(type)
#        info._updateProperty("icon_expr", TYPES_WITH_ICONS[type])


#def setupPortlets(context):
#    """ Setup default portlets for site. """
#    if context.readDataFile('recensio.theme_various.txt') is None:
#        return
#
#    portal = context.getSite()
#    leftColumn = component.getUtility(
#                            IPortletManager, 
#                            name=u'plone.leftcolumn', 
#                            context=portal)
#
#    left = component.getMultiAdapter(
#                            (portal, leftColumn),
#                            IPortletAssignmentMapping, 
#                            context=portal)
#
#    if u'login' in left:
#        del left[u'login']
#
#    if u'extranet_navigation' not in left:
#        left[u'extranet_navigation'] = extranet_navigation.Assignment()



