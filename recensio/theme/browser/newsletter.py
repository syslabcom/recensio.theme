import urllib2

import Acquisition
from DateTime import DateTime
from plone.memoize import instance
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from recensio.translations import RecensioMessageFactory as _
from zope.component import getMultiAdapter


class NewsletterView(BrowserView):
    """View for handling the newsletter subscriptions
    """

    template = ViewPageTemplateFile("templates/newsletter.pt")

    def __call__(self):
        return self.template()

    def subscribe(self, emailaddress, name=""):
        """ helper method to enable mail subscription to anonymous user """
        ptool = getToolByName(self.context, "portal_url")
        portal = ptool.getPortalObject()
        pp = getToolByName(portal, "portal_properties")
        sp = getattr(pp, "site_properties", None)
        siteadmin = getattr(portal, "email_from_address")
        reg_tool = getToolByName(self.context, "portal_registration")

        REQUEST = self.request
        if not emailaddress:
            emailaddress = REQUEST.get("emailaddress", "")
        fullname = REQUEST.get("name", "")
        refererstem = REQUEST.get("HTTP_REFERER").split("?")[0]
        referer = refererstem + "?"
        qs = REQUEST.get("QUERY_STRING", "")
        if qs:
            referer += "?" + qs + "&"

        if reg_tool.isValidEmail(emailaddress):
            pass
        else:
            msg = _(u"You did not enter a valid email address.")
            try:
                msg = unicode(msg, "iso8859-1").encode("utf-8")
            except:
                pass
            return REQUEST.RESPONSE.redirect(referer + "portal_status_message=" + msg)

        if REQUEST.has_key("unsubscribe"):
            try:
                url = "http://lists.recensio.net/mailman/options/newsletter"
                req = urllib2.Request(
                    url=url,
                    data="email=%s&unsubconfirm=1&login-unsub=Unsubscribe"
                    % emailaddress,
                )
                f = urllib2.urlopen(req)
                retval = f.read()
                mssg = _(u"Your unsubscription request has been sent.")
            except Exception, e:
                mssg = (
                    _(u"Your subscription could not be sent. Please try again.")
                    + " "
                    + str(e)
                )
        else:
            try:
                req = urllib2.Request(
                    url="http://lists.recensio.net/mailman/subscribe/newsletter",
                    data="email=%s&fullname=%s&email-button=Subscribe"
                    % (emailaddress, fullname),
                )
                f = urllib2.urlopen(req)
                retval = f.read()
                mssg = _(
                    u"Your subscription request has been sent. Please check your e-mail."
                )
            except Exception, e:
                mssg = (
                    _(u"Your subscription could not be sent. Please try again.")
                    + " "
                    + str(e)
                )

        return REQUEST.RESPONSE.redirect(
            refererstem + "?portal_status_message=%s" % (mssg)
        )
