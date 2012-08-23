""" Viewlets for Recensio.net

 * publicationlisting viewlet

"""

from ZTUtils import make_query
from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
from hashlib import sha256
from DateTime import DateTime
import logging
from Products.CMFCore.utils import getToolByName

log = logging.getLogger(__name__)

def _render_cachekey(method, self):
    portal_membership = getToolByName(self.context, 'portal_membership')
    member = portal_membership.getAuthenticatedMember()
    roles = member.getRolesInContext(self.context)
    today = DateTime().strftime("%Y-%m-%d")
    context_url = self.context.absolute_url()
    return (context_url, roles, today)

class publicationlisting(ViewletBase):
    """ Lists Volumes/Issues/Reviews in the current Publication"""
    implements(IViewlet)

    def __init__(self, context, request, view, manager=None):
        super(publicationlisting, self).__init__(context, request, view, manager)
        try:
            parents = self.request.PARENTS
        except AttributeError:
            return False
        if len(parents)<2:
            return False
        self.parent = self.request.PARENTS[1]

    def visible(self):
        """ should we display at all? """
        if hasattr(self.context, 'portal_type') and \
           self.context.portal_type=='Document' and \
           hasattr(self.parent, 'portal_type') and \
           self.parent.portal_type=='Publication':
            return True
        return False

    def is_expanded(self, uid):
        return uid in self.request.get('expand', [])

    def _make_dict(self, obj):
        "contains the relevant details for listing a Review"
        return dict(
            absolute_url      = obj.absolute_url(),
            effective         = obj.effective(),
            getDecoratedTitle = obj.getDecoratedTitle(lastname_first=False),
            listAuthorsAndEditors = obj.listAuthorsAndEditors(),
            Title             = obj.Title())

    def _get_toggle_link(self, uid):
        expand = self.request.get('expand', [])[:]
        if uid in expand:
            expand.remove(uid)
        else:
            expand.append(uid)
        toggle_link = '%s?%s#%s' % (self.context.absolute_url(),
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

    def _make_issue_dict(self, obj):
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
        volume_objs = self.parent.objectValues('Volume')
        volumes = [{'Title': v.Title(),
                    'id':    v.getId(),
                    'UID':   v.UID(),
                    'toggle_link': self._get_toggle_link(v.UID()),
                    'css_classes': self._get_css_classes(v),
                   } for v in volume_objs]
        return volumes

    def issues(self, volume):
        if not volume in self.parent.objectIds():
            return []
        issue_objs = self.parent[volume].objectValues('Issue')
        issues = [self._make_issue_dict(i) for i in issue_objs]
        return issues
        
    #@ram.cache(_render_cachekey)
    def reviews(self, volume, issue=None):
        if not volume in self.parent.objectIds():
            return []
        if issue is None:
            review_objs = self.parent[volume].objectValues(
                ['ReviewMonograph', 'ReviewJournal'])
        else:
            if not issue in self.parent[volume].objectIds():
                return []
            review_objs = self.parent[volume][issue].objectValues(
                ['ReviewMonograph', 'ReviewJournal'])
        reviews = [self._make_dict(rev) for rev in review_objs]
        return reviews

    def _formatsize(self, size):
        size_kb = size/1024;
        display_size_kb = '{0:n} kB'.format(size_kb) if size_kb > 0 else ''
        display_size_bytes = ' ({0:n} bytes)'.format(size) if display_size_kb else '{0:n} bytes'.format(size)
        display_size = '{0}{1}'.format(display_size_kb, display_size_bytes)
        return display_size

    @ram.cache(lambda method,self,
               reviews: sha256(str([x for x in reviews])).digest())
    def get_volumes(self, reviews):
        def make_dict(obj):
            "contains the relevant details for listing a Review"
            return dict(
                absolute_url      = obj.absolute_url(),
                effective         = obj.effective(),
                getDecoratedTitle = obj.getDecoratedTitle(lastname_first=False),
                listAuthorsAndEditors = obj.listAuthorsAndEditors(),
                Title             = obj.Title())
        volumes = {}
        for review in reviews:
            try:
                review_obj = review.getObject()
            except AttributeError:
                log.error("Solr has search results for an object that does not exist in zodb. This can lead to exceptions. See #4656 how to fix it", exc_info=True)
                continue
            review_parent = review_obj.aq_parent
            if review_parent.portal_type == "Issue":
                # The Issue parent must be a Volume
                volume_obj = review_parent.aq_parent
                if not volumes.has_key(volume_obj.id):
                    volumes[volume_obj.id] = {
                        "Title"     : volume_obj.title,
                        "effective" : volume_obj.effective(),
                        "UID"       : volume_obj.UID()
                        }
                volume = volumes[volume_obj.id]
                if not volume.has_key("issues"):
                    volume["issues"] = {}
                issues = volume["issues"]
                if not issues.has_key(review_parent.id):
                    issues[review_parent.id] = {
                        "Title"     : review_parent.title,
                        "effective" : review_parent.effective(),
                        "UID"       : review_parent.UID()
                        }
                    if "issue.pdf" in review_parent.objectIds():
                        issues[review_parent.id]["pdf"] = review_parent[
                            "issue.pdf"].absolute_url_path()
                        issues[review_parent.id]["pdfsize"] = self._formatsize(
                            review_parent["issue.pdf"].getField(
                                'file').get_size(review_parent["issue.pdf"]))
                issue = issues[review_parent.id]
                issue.setdefault("reviews", []).append(make_dict(review_obj))

            elif review_parent.portal_type == "Volume":
                if not volumes.has_key(review_parent.id):
                    volumes[review_parent.id] = {
                        "Title" : review_parent.title,
                        "UID"   : review_parent.UID()
                        }
                volume = volumes[review_parent.id]
                volume.setdefault("reviews", []).append(make_dict(review_obj))

        # Sort the volumes and issues by changing them into lists and
        # sorting by effective date
        volumes_list = []
        for volume in volumes:
            vol = volumes[volume]
            sorted_reviews = []
            sorted_issues = []
            if vol.has_key("issues"):
                for iss in vol["issues"].values():
                    iss["reviews"] = sorted(
                        iss["reviews"],
                        key=lambda x: x["listAuthorsAndEditors"] and x["listAuthorsAndEditors"][0])
                issues_list = [vol["issues"][i] for i in vol["issues"]]
                sorted_issues = sorted(issues_list,
                                       key=lambda x: x.get("effective",""),
                                       reverse=True)
            if vol.has_key("reviews"):
                sorted_reviews = sorted(
                    vol["reviews"],
                    key=lambda x: x["listAuthorsAndEditors"] and x["listAuthorsAndEditors"][0])

            volumes_list.append({
                    "Title"     : vol.get("Title", ""),
                    "effective" : vol.get("effective", ""),
                    "issues"    : sorted_issues,
                    "reviews"   : sorted_reviews,
                    "UID"       : vol.get("UID", vol.keys()),
                    })

        sorted_volumes  = sorted(volumes_list,
                                 key=lambda x: x.get("effective", ""),
                                 reverse=True)
        return sorted_volumes
