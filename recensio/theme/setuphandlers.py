import logging
from zope import component
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.unsafe_transforms import build_transforms
from plone.registry.interfaces import IRegistry
from collective.xdv.interfaces import ITransformSettings

log = logging.getLogger('recensio.theme.setuphandlers.py')

def setupXDVTheme(context):
    """ Activate and configure collective.xdv
    """
    if context.readDataFile("recensio.theme_various.txt") is None:
        return

    site = context.getSite()
    settings = component.getUtility(IRegistry).forInterface(ITransformSettings)
    settings.enabled = True
    settings.domains = set([u'localhost:8010', u'recensio.syslab.com', u'recensio:8010', u'kielschwein:8010'])
    settings.theme = u'python://recensio.theme/skins/recensio_theme/theme.html'
    settings.rules = u'python://recensio.theme/skins/recensio_theme/rules/default.xml'
    settings.boilerplate = u'python://recensio.theme/skins/recensio_theme/theme.xsl'
    settings.absolute_prefix = unicode(site.getId())
    default_notheme = [
        u'^.*popup$',
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
