from zope.interface import implements
from zope.viewlet.interfaces import IViewlet

from AccessControl import getSecurityManager

from Products.CMFCore.utils import getToolByName
from Products.CMFCore import permissions

from plone.app.layout.viewlets.common import ViewletBase
from plone.app.layout.viewlets.common import SearchBoxViewlet
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

class ViewMixin():
    """ This class provides helpful utility methods for view classes
    """

    def portal_url(self):
        """ """
        return getToolByName(self.context.aq_inner, 'portal_url')()


    def member(self):
        """ """
        pm = getToolByName(self.context.aq_inner, 'portal_membership')
        return pm.getAuthenticatedMember()


class ActionbarPanelViewlet(ViewletBase, ViewMixin):
    """ """
    implements(IViewlet)


class PollViewlet(ViewletBase, ViewMixin):
    """ """
    implements(IViewlet)

    def get_current_poll(self):
        """ Returns the first poll find in the current folder, or None if none
            is found.
        """
        security = getSecurityManager()
        polls = self.context.objectValues('PlonePopoll')
        for poll in polls:
            if security.checkPermission(permissions.View, poll):
                return poll

class ICTSearchBoxViewlet(SearchBoxViewlet):
    index = ViewPageTemplateFile('templates/searchbox.pt')
