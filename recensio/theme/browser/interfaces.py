from zope.interface import Interface


class IRecensioHelperView(Interface):
    """ Interface for the RecensioHelperView """

    def normalize_isbns_in_text(text):
        """Enables flexible full text search for ISBNs"""

    def punctuated_title(self, title, subtitle):
        """ """

    def contains_one_of(self, items, values):
        """ """


class IRedirectToPublication(Interface):
    """ Interface for RedirectToPublication """


class IGeneratePdfRecension(Interface):
    """Interface for PDF generation BrowserView
    """

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """

    def __call__(self):
        """Generate and return a PDF version of the recension
        """

class IBrowseTopics(Interface):
    """Interface for topical browsing (ddcPlace etc.)
    """

    def __call__(self):
        """render the view
        """

class INewsletterView(Interface):
    """ newsletter overview including subscription """

    def subscribe():
        """ subscribe to newsletter """

