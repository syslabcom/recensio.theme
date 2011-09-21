""" Views and functions for Recensio.net
"""
from zope.app.component.hooks import getSite
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implements

from Products.Archetypes.utils import DisplayList
from Products.Five.browser import BrowserView
from plone.i18n.locales.languages import _languagelist
from plone.registry.interfaces import IRegistry

from recensio.contenttypes import contenttypesMessageFactory as _
from recensio.policy.interfaces import IRecensioSettings

from interfaces import IRecensioHelperView



def listRecensioSupportedLanguages():
    portal = getSite()
    vocab = portal.portal_languages.listSupportedLanguages()
    terms = [(x[0], _languagelist[x[0]][u'native']) for x in vocab]
    return DisplayList(terms)

def listAvailableContentLanguages():
    registry = queryUtility(IRegistry)
    settings = registry.forInterface(IRecensioSettings)
    allowed_langs = getattr(
        settings, 'available_content_languages', ''
        ).replace('\r', '').split('\n')
    terms = []
    if allowed_langs != [u""]:
        terms = [(x, _languagelist[x][u'native'])
                 for x in allowed_langs]
    return DisplayList(terms)

def recensioTranslate(msgid):
    portal = getSite()
    language = portal.portal_languages.getPreferredLanguage()
    return translate(Message(msgid, domain="recensio"),
                     target_language=language)

def editorTypes():
    return DisplayList((
            ("herausgeber", recensioTranslate(u"label_abbrev_herausgeber"),),
            ("bearbeiter", recensioTranslate(u"label_abbrev_bearbeiter"),),
            ("redaktion", recensioTranslate(u"label_abbrev_redaktion"),),
            ))

class RecensioHelperView(BrowserView):
    """ General purpose view methods for Recensio """
    implements(IRecensioHelperView)

    @property
    def heading_add_item_title(self):
        """ For French Presentations the add form should display:
        Ajouter une ... """
        portal = getSite()

        fti = portal.portal_types.getTypeInfo(self.context)#
        itemtype = fti.Title()

        lang = portal.portal_languages.getPreferredLanguage()
        if (fti.content_meta_type.startswith("Presentation")
            and lang == "fr"):
            itemtype = "heading_add_%s_title" %fti.content_meta_type

        return itemtype

    def listRecensioSupportedLanguages(self):
        return listRecensioSupportedLanguages()

    def listAvailableContentLanguages(self):
        return listAvailableContentLanguages()


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
