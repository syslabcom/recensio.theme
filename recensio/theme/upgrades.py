import logging
import re

from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from zope.component.hooks import getSite
from zope.component import getUtility
from zope.component import getMultiAdapter

log = logging.getLogger(__name__)

PROFILE = 'profile-recensio.theme:default'


def v1to2(portal_setup):
    portal_setup.runImportStepFromProfile(PROFILE, 'jsregistry')


def v2to3(portal_setup):
    old_re = '<area .*title="Newsletter"[^>]*>[\s]*'\
             '<area .*title="RSS-Feed"[^>]*>'
    new_str = '<area shape="poly" coords="30,90,135,75,128,25,22,35" '\
              'title="RSS-Feed" alt="RSS-Feed" '\
              'href="http://localhost:8010/recensio/RSS-feeds">'
    portal = getSite()
    frontpage = portal.get('front-page')
    column = getUtility(IPortletManager,
                        name=u'plone.rightcolumn',
                        context=frontpage)
    manager = getMultiAdapter((frontpage, column,), IPortletAssignmentMapping)
    postit = manager.get('postit')
    if postit is None:
        log.warn('No postit portlet found, skipping upgrade')
        return
    postit.tal = re.sub(old_re, new_str, postit.tal)
