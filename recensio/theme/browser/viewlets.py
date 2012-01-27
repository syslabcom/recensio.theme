""" Viewlets for Recensio.net

 * publicationlisting viewlet

"""

from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from plone.app.layout.viewlets import ViewletBase
from plone.memoize import ram
from hashlib import sha256
from DateTime import DateTime

class publicationlisting(ViewletBase):
    """ Lists Volumes/Issues/Reviews in the current Publication"""
    implements(IViewlet)

    def visible(self):
        """ should we display at all? """
        try:
            parents = self.request.PARENTS
        except AttributeError:
            return False
        if len(parents)<2:
            return False
        parent = self.request.PARENTS[1]
        if hasattr(self.context, 'portal_type') and \
           self.context.portal_type=='Document' and \
           hasattr(parent, 'portal_type') and \
           parent.portal_type=='Publication':
            return True
        return False

    @ram.cache(lambda method, self: DateTime().Date())
    def volumes(self):
        """ Return a tree of Reviews for the current publication

        Reviews are contained within a tree of Volumes and Issues
        under each Publication
         * Volumes may contain Issues and Reviews
         * Issues may only contain Reviews

        {"vol_1" : {
                "title" : "Volume 1",
                "reviews" : [
                    review_obj_1, review_obj_2
                    ],
                "issues" : {
                    "issue_1": {
                        "title" : "Issue 1",
                        "reviews" : [
                            review_obj_1, review_obj_2
                            ]}
                    }
         }

         """

        catalog = self.context.portal_catalog
        path = '/'.join(self.context.getPhysicalPath()[:-1])
        query = {"b_size" : 10000}
        query["path"] = {"query" : path}
        query["portal_type"] = ("Review Journal",
                                "Review Monograph")
        query["sort_on"] = "effective"
        query["sort_order"] = "descending"
        reviews = catalog(query)

        volumes = self.get_volumes(reviews)
        return volumes

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
                listAuthors       = obj.listAuthors(),
                Title             = obj.Title())
        volumes = {}
        for review in reviews:
            review_obj = review.getObject()
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
                        key=lambda x: x["listAuthors"] and x["listAuthors"][0])
                issues_list = [vol["issues"][i] for i in vol["issues"]]
                sorted_issues = sorted(issues_list,
                                       key=lambda x: x.get("effective",""),
                                       reverse=True)
            if vol.has_key("reviews"):
                sorted_reviews = sorted(
                    vol["reviews"],
                    key=lambda x: x["listAuthors"] and x["listAuthors"][0])

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
