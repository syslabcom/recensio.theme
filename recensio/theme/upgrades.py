import logging
import re

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import IPortletManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite

log = logging.getLogger(__name__)

PROFILE = "profile-recensio.theme:default"


def v1to2(portal_setup):
    portal_setup.runImportStepFromProfile(PROFILE, "jsregistry")


def v2to3(portal_setup):
    newsletter_re = r'[ \t]*<area .*title="Newsletter"[^>]*>\s*\n'
    rss_re = '(<area [^>]*) coords="[0-9,]*" ([^>]*RSS-Feed[^>]*>)'
    rss_re2 = '(<area [^>]*RSS-Feed[^>]*) coords="[0-9,]*" ([^>]*>)'
    new_rss_str = r'\1 coords="30,90,135,75,128,25,22,35" \2'
    portal = getSite()
    frontpage = portal.get("front-page")
    translations = frontpage.getTranslations().values()
    for fp_trans, status in translations:
        column = getUtility(
            IPortletManager, name=u"plone.rightcolumn", context=fp_trans
        )
        manager = getMultiAdapter((fp_trans, column,), IPortletAssignmentMapping)
        postit = manager.get("postit")
        if postit is None:
            log.warn(
                "No postit portlet found for {0}, "
                "skipping upgrade".format(fp_trans.Language())
            )
            return
        postit.tal = re.sub(newsletter_re, "", postit.tal)
        postit.tal = re.sub(rss_re, new_rss_str, postit.tal)
        postit.tal = re.sub(rss_re2, new_rss_str, postit.tal)
