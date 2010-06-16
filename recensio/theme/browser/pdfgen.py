from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
import logging
import tempfile
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.lib.colors import grey

log = logging.getLogger('recensio.theme/browser/pdfgen.py')

class GeneratePdfRecension(BrowserView):
    """View to generate PDF cover sheets
    """

    def __call__(self):
        return self.genPdfRecension()

    def _prepareHeader(self, contentlength, filename='recension.pdf'):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader('content-disposition', 'inline; filename="%s"' % filename)
        R.setHeader('content-length', str(contentlength))

    def _genCoverSheet(self):
        tmpfile,tmppath = tempfile.mkstemp(prefix='cover', suffix='.pdf')
        cover = canvas.Canvas(tmpfile, pagesize=A4)
        pwidth,pheight = A4
        cover.drawImage(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'images/logo2_fuer-Deckblatt.jpg'), 0, pheight-4.21*cm, width=28.28*cm, height=4.21*cm)
        cover.drawImage(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'images/logo_icon_watermark.jpg'), pwidth/2.-.5*13.76*cm, pheight/2-.5*13.76*cm, width=13.76*cm, height=13.76*cm, preserveAspectRatio=True, anchor='c')
        
        #cover.setFont('Garamond', 12)
        cover.setFillColor(grey)
        cover.drawString(2.50*cm, pheight-5.5*cm, 'citation style')
        cover.drawString(2.50*cm, pheight-21.5*cm, 'copyright')

        cover.showPage()
        return cover.getpdfdata()

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """
        pdfdata = self._genCoverSheet()
        self._prepareHeader(len(pdfdata))
        return pdfdata
