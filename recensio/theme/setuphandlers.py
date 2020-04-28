import logging
from zope import component
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from Products.CMFCore.utils import getToolByName
from Products.PortalTransforms.unsafe_transforms import build_transforms
from plone.registry.interfaces import IRegistry

log = logging.getLogger("recensio.theme.setuphandlers.py")


def addUnsafeTransforms(context):
    """ Add transforms that are considered unsafe to portal_transforms
    """
    if context.readDataFile("recensio.theme_various.txt") is None:
        return

    portal_transforms = getToolByName(context, "portal_transforms", None)
    if portal_transforms:
        log.info("calling build_transforms.initialize()")
        build_transforms.initialize(portal_transforms)
    else:
        log.warn("no portal_transforms found, not adding unsafe transfers")
