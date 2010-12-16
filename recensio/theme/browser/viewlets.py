from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase

class publicationlisting(ViewletBase):
    implements(IViewlet)

    def visible(self):
        """ should we display at all? """
        try:
            parents = self.request.PARENTS
        except AttributeError:
            return False
        if len(parents)<2:
            return False
        parent = self.request.PARENTS[1]
        if hasattr(self.context, 'portal_type') and \
           self.context.portal_type=='Document' and \
           hasattr(parent, 'portal_type') and \
           parent.portal_type=='Publication':
            return True
        return False
        
    def volumes(self):
        """ return a mapping of all volumes including contained issues and reviews """
        try:
            parent = self.request.PARENTS[1]
        except AttributeError:
            parent = None
        if not hasattr(parent, 'objectValues'):
            return []
        def sortedObjectValues(container, *constraints):
            retval = [x for x in container.objectValues(constraints)]
            retval.sort(lambda a, b: b.effective().__cmp__(a.effective()))
            return retval

        volumes = []
        for volume in sortedObjectValues(parent, 'Volume'):
            issues = []
            for issue in sortedObjectValues(volume, 'Issue'):
                issuechildren = sortedObjectValues(issue, 'ReviewJournal', 'ReviewMonograph')
                issues.append(dict(title=issue.Title(), children=issuechildren))
            
            volumechildren = dict(issues=issues, reviews=sortedObjectValues(volume, 'ReviewJournal', 'ReviewMonograph'))
            volumes.append(dict(title=volume.Title(), children=volumechildren))
        return volumes
  
