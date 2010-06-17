# vim:fileencoding=utf8
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

    def __init__(self):
        self.copyright = u"This article may be downloaded and/or used within the private copying\nexemption. Any further use without permission of the rights shall be subject to\nlegal licences (§§ 44a-63a UrhG / German Copyright Act).\n\nDieser Beitrag kann vom Nutzer zu eigenen nicht-kommerziellen Zwecken\nheruntergeladen und/oder ausgedruckt werden. Darüber hinaus gehende\nNutzungen sind ohne weitere Genehmigung der Rechteinhaber nur im Rahmen\nder gesetzlichen Schrankenbestimmungen (§§ 44a-63a UrhG) zulässig."

        self.metadata_template = u"%(author_rec)s: review of: %(author_book)s, %(title)s, \
%(location)s: %(publisher)s %(year)s, in: %(title_collection) \
Band %(no_collection)s, p. %(pages_collection)s, http://www.recensio.net/%(url)s"

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
        
        cover.setFont('Helvetica', 10)
        cover.setFillColor(grey)
        cover.drawString(2.50*cm, pheight-5.5*cm, u'citation style')
        cover.drawString(2.50*cm, pheight-21.5*cm, u'copyright')

        copyright_txt = cover.beginText(6.20*cm, pheight-22.5*cm)
        copyright_txt.textLines(self.copyright)
        cover.drawText(copyright_txt)

        cover.showPage()
        return cover.getpdfdata()

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """
        pdfdata = self._genCoverSheet()
        self._prepareHeader(len(pdfdata))
        return pdfdata
