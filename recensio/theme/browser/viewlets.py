""" Viewlets for Recensio.net

 * publicationlisting viewlet

"""

from DateTime import DateTime
from plone.app.layout.nextprevious import view as npview
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from ZTUtils import make_query
import logging

log = logging.getLogger(__name__)


def _render_cachekey(method, self, volume, issue=None):
    portal_membership = getToolByName(self.context, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()
    roles = member.getRolesInContext(self.context)
    today = DateTime().strftime("%Y-%m-%d")
    context_url = self.context.absolute_url()
    return (context_url, roles, today, volume, issue)


class publicationlisting(ViewletBase):
    """ Lists Volumes/Issues/Reviews in the current Publication"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager=None):
        super(publicationlisting, self).__init__(
            context, request, view, manager)
        try:
            parents = self.request.PARENTS
        except AttributeError:
            return False
        if len(parents) < 2:
            return False
        self.parent = self.request.PARENTS[1]

    def visible(self):
        """ should we display at all? """
        if hasattr(self.context, 'portal_type') and \
           self.context.portal_type == 'Document' and \
           hasattr(self.parent, 'portal_type') and \
           self.parent.portal_type == 'Publication':
            return True
        return False

    def is_expanded(self, uid):
        return uid in self.request.get('expand', [])

    def _make_dict(self, obj):
        "contains the relevant details for listing a Review"
        return {
            'absolute_url':          obj.absolute_url(),
            'effective':             obj.effective(),
            'getDecoratedTitle':     obj.getDecoratedTitle(
                lastname_first=False),
            'listAuthorsAndEditors': obj.listAuthorsAndEditors(),
            'Title':                 obj.Title()
        }

    def _get_toggle_link(self, uid):
        expand = self.request.get('expand', [])[:]
        if uid in expand:
            expand.remove(uid)
        else:
            expand.append(uid)
        toggle_link = '%s?%s#%s' % (
            self.context.absolute_url(),
            make_query(expand=expand),
            uid)
        return toggle_link

    def _get_css_classes(self, obj):
        css_classes = []
        if len(obj.objectIds(['ReviewMonograph', 'ReviewJournal'])) > 0:
            css_classes.append('review_container')
            if self.is_expanded(obj.UID()):
                css_classes.append('expanded')
        return ' '.join(css_classes) or None

    def _make_iss_or_vol_dict(self, obj):
        issue_dict = {'Title':  obj.Title(),
                      'id':     obj.getId(),
                      'UID':    obj.UID(),
                      'toggle_link': self._get_toggle_link(obj.UID()),
                      'css_classes': self._get_css_classes(obj),
                      }

        if "issue.pdf" in obj.objectIds():
            issue_dict['pdf'] = obj["issue.pdf"].absolute_url_path()
            issue_dict['pdfsize'] = self._formatsize(obj["issue.pdf"].getField(
                'file').get_size(obj["issue.pdf"]))
        return issue_dict

    def volumes(self):
        objects = self.parent.getFolderContents(
            {'portal_type': 'Volume'},
            full_objects=True)
        volume_objs = sorted(objects,
                             key=lambda v: v.effective(),
                             reverse=True)
        volumes = [self._make_iss_or_vol_dict(v) for v in volume_objs]
        return volumes

    def issues(self, volume):
        if not volume in self.parent.objectIds():
            return []
        objects = self.parent[volume].getFolderContents(
            {'portal_type': 'Issue'},
            full_objects=True)
        issue_objs = sorted(objects, key=lambda v: v.effective(), reverse=True)
        issues = [self._make_iss_or_vol_dict(i) for i in issue_objs]
        return issues

    @ram.cache(_render_cachekey)
    def reviews(self, volume, issue=None):
        if not volume in self.parent.objectIds():
            return []
        if issue is None:
            review_objs = self.parent[volume].getFolderContents(
                {'portal_type': ['Review Monograph', 'Review Journal']},
                full_objects=True)
        else:
            if not issue in self.parent[volume].objectIds():
                return []
            review_objs = self.parent[volume][issue].getFolderContents(
                {'portal_type': ['Review Monograph', 'Review Journal']},
                full_objects=True)
        review_objs = sorted(review_objs,
                             key=lambda v: v.listAuthorsAndEditors())
        reviews = [self._make_dict(rev) for rev in review_objs]
        return reviews

    def _formatsize(self, size):
        size_kb = size / 1024
        display_size_kb = '{0:n} kB'.format(size_kb) if size_kb > 0 else ''
        if display_size_kb:
            display_size_bytes = ' ({0:n} bytes)'.format(size)
        else:
            display_size_bytes = '{0:n} bytes'.format(size)
        display_size = '{0}{1}'.format(display_size_kb, display_size_bytes)
        return display_size


class NextPreviousViewlet(npview.NextPreviousViewlet):
    index = ZopeTwoPageTemplateFile('templates/nextprevious.pt')
