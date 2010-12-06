from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets import ViewletBase

class publicationlisting(ViewletBase):
    implements(IViewlet)

    def visible(self):
        """ should we display at all? """
        parent = self.request.PARENTS[1]
        if self.context.portal_type=='Document' and parent.portal_type=='Publication':
            return True
        return False
        
    def volumes(self):
        """ return a mapping of all volumes including contained issues and reviews """
        parent = self.request.PARENTS[1]
        if not hasattr(parent, 'objectValues'):
            return []
        volumes = []
        for volume in parent.objectValues('Volume'):
            issues = []
            for issue in volume.objectValues('Issue'):
                issuechildren = issue.objectValues(['ReviewJournal', 'ReviewMonograph'])
                issues.append(dict(title=issue.Title(), children=issuechildren))
            
            volumechildren = dict(issues=issues, reviews=volume.objectValues(['ReviewJournal', 'ReviewMonograph']))
            volumes.append(dict(title=volume.Title(), children=volumechildren))
        return volumes
  