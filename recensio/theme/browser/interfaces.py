from zope.interface import Interface


class IRecensioHelperView(Interface):
    """Interface for the RecensioHelperView"""

    def normalize_isbns_in_text(text):
        """Enables flexible full text search for ISBNs"""

    def punctuated_title(self, title, subtitle):
        """ """

    def contains_one_of(self, items, values):
        """ """

    def get_subtree(self, value):
        """ """


class IRedirectToPublication(Interface):
    """Interface for RedirectToPublication"""


class IGeneratePdfRecension(Interface):
    """Interface for PDF generation BrowserView"""

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension"""

    def __call__(self):
        """Generate and return a PDF version of the recension"""


class IBrowseTopics(Interface):
    """Interface for topical browsing (ddcPlace etc.)"""

    def __call__(self):
        """render the view"""


class INewsletterView(Interface):
    """newsletter overview including subscription"""

    def subscribe():
        """subscribe to newsletter"""


class IFilterSearchView(Interface):
    """Interface for FilterSearchView"""

    def __call__():
        """Render the view"""

    def sort(submenu):
        """Sort submenu"""

    def get_foreign_url(result):
        """Get the external URL of a search result from another portal"""

    def get_portal_link_snippet():
        """Get a comma snippet of HTML with a comma separated list of links to
        all available portals"""
