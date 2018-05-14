""" Views and functions for Recensio.net
"""
import re
from zope.component.hooks import getSite
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implements

from Products.Archetypes.utils import DisplayList
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.locales.languages import _languagelist
from plone.registry.interfaces import IRegistry

from recensio.contenttypes import contenttypesMessageFactory as _
from recensio.contenttypes.browser.canonical import CanonicalURLHelper
from recensio.contenttypes.interfaces.review import IParentGetter
from recensio.policy.interfaces import IRecensioSettings

from interfaces import IRecensioHelperView, IRedirectToPublication


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
        terms.sort()
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

    def punctuated_title(self, title, subtitle):
        """ #4040

        if the string already ends in an punctuation mark don't add
        another """
        last_char = title[-1]

        p_title = title
        if last_char not in ["!", "?", ":", ";", ".", ","] and subtitle:
            p_title = p_title + "."

        if subtitle:
            p_title = p_title + " "

        return p_title

    def normalize_isbns_in_text(self, text):
        expr = re.compile(u'[0-9]+[ \-0-9]*[0-9]+')
        for match in expr.findall(text):
            isbn = match
            isbn = ''.join(isbn.split('-'))
            isbn = ''.join(isbn.split(' '))
            text = text.replace(match, isbn)
        return text

    def contains_one_of(self, items, values):
        """Check whether one of the values is contained in items. items must be
        a list of tuples as acquired by calling items() on a vocabulary dict.
        """
        return sum(
            [item[0] in values or
             self.contains_one_of(dict(item[1][1] or {}).items(), values)
             for item in items])


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

class RedirectToPublication(BrowserView):
    implements(IRedirectToPublication)

    def __call__(self):
        pub = IParentGetter(self).get_parent_object_of_type("Publication")
        uid = self.context.UID()
        return self.request.RESPONSE.redirect(pub.absolute_url()+
                                              "?expand:list="+uid+"#"+uid)


class DatenschutzView(BrowserView):
    template = ViewPageTemplateFile('templates/datenschutz.pt')
    template_piwik_opt_out = ViewPageTemplateFile('templates/piwik_opt_out.pt')

    def __call__(self):
        return self.template(self)

    def getText(self):
        base_text = safe_unicode(self.context.getText())
        if u'[PIWIK-OPT-OUT]' in base_text:
            text = base_text.replace(
                u'[PIWIK-OPT-OUT]',
                self.template_piwik_opt_out(self),
            )
        else:
            text = '\n'.join((base_text, self.template_piwik_opt_out(self)))
        return text


class EnsureCanonical(BrowserView, CanonicalURLHelper):

    def __call__(self):
        canonical_url = self.get_canonical_url()
        if canonical_url != self.request['ACTUAL_URL']:
            return self.request.response.redirect(canonical_url, status=301)
        return self.context()
