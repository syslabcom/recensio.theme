from zope.interface import Interface
from plone.theme.interfaces import IDefaultPloneLayer

class IThemeSpecific(IDefaultPloneLayer):
    """Marker interface that defines a Zope 3 browser layer.
    """

class IRecensioLayer(Interface):
    """Marker Interface for a custom BrowserLayer
    """

class IGeneratePdfRecension(Interface):
    """Interface for PDF generation BrowserView
    """
    
    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """

    def __call__(self):
        """Generate and return a PDF version of the recension
        """

