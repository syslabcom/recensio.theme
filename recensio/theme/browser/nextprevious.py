from zope.interface import implements
from zope.component import adapts

from Products.ATContentTypes.browser.nextprevious import ATFolderNextPrevious

from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from recensio.contenttypes.content.issue import Issue

class RecensioFolderNextPrevious(ATFolderNextPrevious):
    """ Use EffectiveDate to determine next/previous instead of 
        getObjPositionInParent """
    implements(INextPreviousProvider)
    adapts(Issue)

    @property
    def enabled(self):
        return True
    
    @memoize
    def itemRelatives(self, oid):
        """Get the relative next and previous items
        """
        catalog  = getToolByName(self.context, 'portal_catalog')
        obj = self.context[oid]
        path = '/'.join(obj.getPhysicalPath())

        previous = None
        next     = None

        result = sorted(catalog(self.buildNextPreviousQuery()),
                            key=lambda x: x["listAuthorsAndEditors"] and x["listAuthorsAndEditors"][0])
        if result and len(result) > 1:
            index = [x.getPath() for x in result].index(path)
            if index - 1 >= 0:
                previous = self.buildNextPreviousItem(result[index - 1])
            if index + 1 < len(result):
                next = self.buildNextPreviousItem(result[index + 1])

        nextPrevious = {
            'next'      : next,
            'previous'  : previous,
            }

        return nextPrevious
        
    def buildNextPreviousQuery(self):
        query                    = {}
        query['portal_type']     = [
            'Presentation Online Resource', 'Presentation Article Review',
            'Presentation Collection', 'Presentation Monograph',
            'Review Journal', 'Review Monograph',
                ]
        query['path']            = dict(query = '/'.join(self.context.getPhysicalPath()),
                                        depth = 1)
                
        # Filters on content
        query['is_default_page'] = False
        query['is_folderish']    = False

        return query

