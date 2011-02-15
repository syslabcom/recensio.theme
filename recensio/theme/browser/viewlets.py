""" Viewlets for Recensio.net

 * publicationlisting viewlet

"""

from zope.interface import implements
from zope.viewlet.interfaces import IViewlet
from plone.app.layout.viewlets import ViewletBase

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
        query = {}
        query["path"] = {"query" : path}
        query["portal_type"] = ("Review Journal",
                                "Review Monograph")
        query["sort_on"] = "effective"
        reviews = catalog(query)

        volumes = {}
        for review in reviews:
            review_obj = review.getObject()
            review_parent = review_obj.aq_parent
            if review_parent.portal_type == "Issue":
                # The parent must be a Volume
                volume_obj = review_parent.aq_parent
                if not volumes.has_key(volume_obj.id):
                    volumes[volume_obj.id] = { "Title" : volume_obj.title }
                volume = volumes[volume_obj.id]
                if not volume.has_key("issues"):
                    volume["issues"] = {}
                issues = volume["issues"]
                if not issues.has_key(review_parent.id):
                    issues[review_parent.id] = { "Title" : review_parent.title }
                issue = issues[review_parent.id]
                issue.setdefault("reviews", []).append(review_obj)

            elif review_parent.portal_type == "Volume":
                if not volumes.has_key(review_parent.id):
                    volumes[review_parent.id] = {
                        "Title" : review_parent.title }
                volume = volumes[review_parent.id]
                volume.setdefault("reviews", []).append(review_obj)

        return volumes
