from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize.instance import memoize
from Products.ATContentTypes.browser.nextprevious import ATFolderNextPrevious
from Products.CMFCore.utils import getToolByName
from recensio.contenttypes.config import REVIEW_TYPES
from recensio.contenttypes.interfaces import IIssue
from recensio.contenttypes.interfaces import IVolume
from zope.component import adapts
from zope.interface import implements


class RecensioFolderNextPrevious(ATFolderNextPrevious):
    """Use EffectiveDate to determine next/previous instead of
    getObjPositionInParent"""

    implements(INextPreviousProvider)

    @property
    def enabled(self):
        return True

    @memoize
    def itemRelatives(self, oid):
        """Get the relative next and previous items"""
        catalog = getToolByName(self.context, "portal_catalog")
        obj = self.context[oid]
        path = "/".join(obj.getPhysicalPath())

        previous = None
        next = None

        result = sorted(
            catalog(self.buildNextPreviousQuery()),
            key=lambda x: x.get("listAuthorsAndEditors", [])
            and x["listAuthorsAndEditors"][0],
        )
        if result and len(result) > 1:
            pathlist = [x.getPath() for x in result]
            if path in pathlist:
                index = pathlist.index(path)
                if index - 1 >= 0:
                    previous = self.buildNextPreviousItem(result[index - 1])
                if index + 1 < len(result):
                    next = self.buildNextPreviousItem(result[index + 1])

        nextPrevious = {
            "next": next,
            "previous": previous,
        }

        return nextPrevious

    def buildNextPreviousQuery(self):
        query = {}
        query["portal_type"] = REVIEW_TYPES
        query["path"] = dict(query="/".join(self.context.getPhysicalPath()), depth=1)
        query["b_size"] = 10000

        # Filters on content
        query["is_default_page"] = False
        query["is_folderish"] = False

        return query


class RecensioVolumeNextPrevious(RecensioFolderNextPrevious):
    adapts(IVolume)


class RecensioIssueNextPrevious(RecensioFolderNextPrevious):
    adapts(IIssue)
