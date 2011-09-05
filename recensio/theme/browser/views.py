from Products.Five.browser import BrowserView
from zope.app.component.hooks import getSite
from zope.interface import implements

from interfaces import IRecensioHelperView


class RecensioHelperView(BrowserView):
    """ General purpose view methods for Recensio """
    implements(IRecensioHelperView)

    @property
    def heading_add_item_title(self):
        """ For French Presentations the add form should display:
        Ajouter une ... """
        portal = getSite()
        fti = portal.portal_types.getTypeInfo(self.context)#
        lang = portal.portal_languages.getPreferredLanguage()
        if (fti.content_meta_type.startswith("Presentation")
            and lang == "fr"):
            return "heading_add_%s_title" %fti.content_meta_type
        return fti.Title()


class CreateNewPresentationView(BrowserView):
    """ Helper to direct to new presentation creation """

    def __call__(self):
        membersfolder = self.context.portal_membership.getMembersFolder()
        homefolder = self.context.portal_membership.getHomeFolder()
        if homefolder is None:
            return self.request.RESPONSE.redirect('login_form')
        return self.request.RESPONSE.redirect(
            membersfolder.absolute_url()+'/add_new_item')


class ManageMyPresentationsView(BrowserView):
    """ Helper to direct to my presentations """

    def __call__(self):
        homefolder = self.context.portal_membership.getHomeFolder()
        if homefolder is None:
            return self.request.RESPONSE.redirect('login_form')
        return self.request.RESPONSE.redirect(homefolder.absolute_url())
