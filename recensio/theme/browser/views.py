from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces import Unauthorized


class CreateNewPresentationView(BrowserView):
    """ Helper to direct to new presentation creation """

    def __call__(self):
        membersfolder = self.context.portal_membership.getMembersFolder()
        homefolder = self.context.portal_membership.getHomeFolder()
        if homefolder is None:
            return self.request.RESPONSE.redirect('login_form')
        return self.request.RESPONSE.redirect(membersfolder.absolute_url()+'/add_new_item')

class ManageMyPresentationsView(BrowserView):
    """ Helper to direct to my presentations """

    def __call__(self):
        homefolder = self.context.portal_membership.getHomeFolder()
        if homefolder is None:
            return self.request.RESPONSE.redirect('login_form')
        return self.request.RESPONSE.redirect(homefolder.absolute_url())
