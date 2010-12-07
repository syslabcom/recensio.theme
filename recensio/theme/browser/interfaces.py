from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

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
        