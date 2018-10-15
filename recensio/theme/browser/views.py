""" Views and functions for Recensio.net
"""
import logging
import re
from Acquisition import aq_parent
from ZTUtils import make_query
from zope.component.hooks import getSite
from zope.component.hooks import setSite
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate
from zope.i18nmessageid import Message
from zope.interface import implements

from Products.Archetypes.utils import DisplayList
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.i18n.locales.languages import _languagelist
from plone.memoize import instance
from plone.registry.interfaces import IRegistry

from recensio.contenttypes import contenttypesMessageFactory as _
from recensio.contenttypes.browser.canonical import CanonicalURLHelper
from recensio.contenttypes.interfaces.review import IParentGetter
from recensio.policy.interfaces import IRecensioSettings

from interfaces import IRecensioHelperView, IRedirectToPublication

log = logging.getLogger(__name__)


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


class SwitchPortal(object):
    def __init__(self, portal):
        self.portal = portal

    def __enter__(self):
        self.original_portal = getSite()
        setSite(self.portal)

    def __exit__(self, type, value, traceback):
        setSite(self.original_portal)
        if value:
            log.warn('Could not get portal url of ' + self.portal.id,
                     exc_info=(type, value, traceback))
            return True


class CrossPlatformMixin(object):

    def get_toggle_cross_portal_url(self):
        new_form = self.request.form.copy()
        new_form['use_navigation_root'] = not new_form.get('use_navigation_root', True)
        return '?'.join((self.request['ACTUAL_URL'], make_query(new_form)))

    @instance.memoize
    def get_foreign_portal_url(self, portal_id):
        other_portal = self.context.unrestrictedTraverse('/' + portal_id)
        external_url = None
        with SwitchPortal(other_portal):
            registry = getUtility(IRegistry)
            recensio_settings = registry.forInterface(IRecensioSettings)
            external_url = recensio_settings.external_portal_url
        return external_url

    def get_foreign_url(self, result):
        portal_id = result.getPath().split('/')[1]
        other_portal = self.context.unrestrictedTraverse('/' + portal_id)
        external_url = self.get_foreign_portal_url(portal_id)
        if not external_url:
            return result.getURL()
        return result.getURL().replace(
            other_portal.absolute_url(), external_url)

    @instance.memoize
    def get_all_portal_ids(self):
        this_portal = getSite()
        app = aq_parent(this_portal)
        return app.objectIds('Plone Site')

    def get_portal_link_snippet(self):
        portal_ids = self.get_all_portal_ids()
        link_tpl = '<a href="{1}">{0}</a>'
        portal_infos = []
        for portal_id in portal_ids:
            portal_title = self.context.restrictedTraverse('/' + portal_id).Title()
            portal_infos.append(
                (portal_title, self.get_foreign_portal_url(portal_id)))
        link_snippet = ', '.join([
            link_tpl.format(*portal_info) for portal_info in portal_infos
            if portal_info[1]])
        return link_snippet
