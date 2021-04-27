from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import utils
from Products.CMFPlone.browser.interfaces import INavigationBreadcrumbs
from Products.CMFPlone.browser.navigation import PhysicalNavigationBreadcrumbs
from recensio.contenttypes.interfaces.issue import IIssue
from recensio.contenttypes.interfaces.review import IParentGetter
from recensio.contenttypes.interfaces.volume import IVolume
from zope.component import getMultiAdapter
from zope.interface import implements


class RecensioNavigationBreadcrumbs(PhysicalNavigationBreadcrumbs):
    implements(INavigationBreadcrumbs)

    def breadcrumbs(self):
        """Shows publications and their volumes and issues as plain text
        (without a link) if the user has no permission to view them."""
        context = aq_inner(self.context)
        pm = getToolByName(self.context, "portal_membership")
        user = pm.getAuthenticatedMember()

        if IVolume.providedBy(context) or IIssue.providedBy(context):
            pub = IParentGetter(context).get_parent_object_of_type("Publication")
            if user.has_permission("View", pub):
                return super(RecensioNavigationBreadcrumbs, self).breadcrumbs()
        elif user.has_permission("View", context):
            return super(RecensioNavigationBreadcrumbs, self).breadcrumbs()

        request = self.request
        container = utils.parent(context)
        view = getMultiAdapter((container, request), name="breadcrumbs_view")
        base = tuple(view.breadcrumbs())
        base += (
            {
                "absolute_url": "",
                "Title": utils.pretty_title_or_id(context, context),
            },
        )
        return base
