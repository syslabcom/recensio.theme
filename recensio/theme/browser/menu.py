from plone.app.contentmenu.menu import WorkflowSubMenuItem
from plone.memoize.instance import memoize


class ICTWorkflowSubMenuItem(WorkflowSubMenuItem):
    """ Overwriting the available method because we DO want to show the
        workflow submenu on folder_contents """

    @memoize
    def available(self):
        return (self.context_state.workflow_state() is not None)
