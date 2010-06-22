import logging
from zope import component
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.unsafe_transforms import build_transforms
from plone.registry.interfaces import IRegistry
from collective.xdv.interfaces import ITransformSettings

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

def setupXDVTheme(context):
    """ Activate and configure collective.xdv
    """
    if context.readDataFile("recensio.theme_various.txt") is None:
        return

    site = context.getSite()
    settings = component.getUtility(IRegistry).forInterface(ITransformSettings)
    settings.enabled = True
    settings.domains = set([u'localhost:8010', u'recensio.syslab.com', u'recensio:8010'])
    settings.theme = u'python://recensio.theme/skins/recensio_theme/theme.html'
    settings.rules = u'python://recensio.theme/skins/recensio_theme/rules/default.xml'
    settings.boilerplate = u'python://recensio.theme/skins/recensio_theme/theme.xsl'
    settings.absolute_prefix = unicode(site.getId())
    default_notheme = [
        u'^.*/emptypage$',
        u'^.*/manage$',
        u'^.*/manage_(?!translations_form)[^/]+$',
        u'^.*/image_view_fullscreen$',
        u'^.*/refbrowser_popup(\?.*)?$',
        u'^.*/error_log(/.*)?$',
        u'^.*/aq_parent(/.*)?$',
        u'^.*/portal_javascripts/.*/jscripts/tiny_mce/.*$',
        u'^.*/tinymce-upload$',
        u'^.*/.+/plone(image|link)\.htm$',
        u'^.*/plugins/table/(table|row|cell|merge_cells)\.htm$',
        u'^.*/plugins/searchreplace/searchreplace.htm$',
        u'^.*/.+/advanced/(source_editor|anchor)\.htm$',
        u'^.*/@@babblechat.*$',       # Don't interfere with Babble
        u'^.*/@@render_chat_box',     # Don't interfere with Babble
        u'^.*/manage_addProduct/.*$', # Necesary for ZMI access.
        ]

    if settings.notheme != None:
        settings.notheme = set(default_notheme)
    else:
        for i in default_notheme:
            # Add / re-add any which are missing from the default
            # configuration, this won't remove additional entries
            # which may have been added manually
            settings.notheme = settings.notheme.add(i)

def addUnsafeTransforms(context):
    """ Add transforms that are considered unsafe to portal_transforms
    """
    if context.readDataFile("recensio.theme_various.txt") is None:
        return

    portal_transforms = getToolByName(context, 'portal_transforms', None)
    if portal_transforms:
        log.info('calling build_transforms.initialize()')
        build_transforms.initialize(portal_transforms)
    else:
        log.warn('no portal_transforms found, not adding unsafe transfers')
