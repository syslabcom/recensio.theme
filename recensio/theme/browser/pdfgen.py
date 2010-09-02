from Products.statusmessages.interfaces import IStatusMessage
# vim:fileencoding=utf8
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

import logging
import tempfile
import os
from pkg_resources import resource_filename

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import cm
from reportlab.lib.colors import grey
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

log = logging.getLogger('recensio.theme/pdfgen.py')

COPYRIGHT = u"""This article may be downloaded and/or used within the private copying
exemption. Any further use without permission of the rights shall be subject to
legal licences (§§ 44a-63a UrhG / German Copyright Act).

Dieser Beitrag kann vom Nutzer zu eigenen nicht-kommerziellen Zwecken
heruntergeladen und/oder ausgedruckt werden. Darüber hinaus gehende
Nutzungen sind ohne weitere Genehmigung der Rechteinhaber nur im Rahmen
der gesetzlichen Schrankenbestimmungen (§§ 44a-63a UrhG) zulässig."""

class GeneratePdfRecension(BrowserView):
    """View to generate PDF cover sheets
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        try:
            cover = self.genPdfRecension()
            pdf = self.context.get_review_pdf()
            original = pdf.open().name
            new = tempfile.mkstemp(prefix = 'final', suffix = '.pdf')[1]
            error_code = os.system('ulimit -t 5;pdftk %s %s cat output %s' % (cover, original, new))
            if error_code:
                IStatusMessage(self.request).add('Creating the pdf has failed! Please try again or ask for support', 'error')
                return
            pdfdata = file(new).read()
        finally:
            os.remove(cover)
            os.remove(new)
        self._prepareHeader(len(pdfdata))
        return pdfdata

    def _prepareHeader(self, contentlength, filename='recension.pdf'):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader('content-disposition', 'inline; filename="%s"' % filename)
        R.setHeader('content-length', str(contentlength))

    def _drawImage(self, filename, x, y, width, height, **kw):
        fullPath = resource_filename(__name__, os.path.join('images', filename))
        self.canvas.drawImage(fullPath,
            x, y, width, height,
            **kw)

    def _genCoverSheet(self):
        file_handle, tmpfile = tempfile.mkstemp(prefix='cover', suffix='.pdf')
        self.canvas = cover = canvas.Canvas(tmpfile, pagesize=A4)
        pwidth,pheight = A4

        # register the font (unicode-aware)
        arial =  os.path.abspath(__file__ + '/../../data/arial.ttf')
        pdfmetrics.registerFont( TTFont('Arial', arial) )

        self._drawImage('logo2_fuer-Deckblatt.jpg', 0, pheight - 4.21*cm,
            28.28*cm, 4.21*cm)
        self._drawImage('logo_icon_watermark.jpg', pwidth/2.0 - 5*13.76*cm,
            pheight/2.5 * 13.76*cm, 13.76*cm, 13.76*cm, preserveAspectRatio=True,
            anchor='c')
        cover.setFont('Arial', 10)
        cover.setFillColor(grey)
        cover.drawString(2.50*cm, pheight-5.5*cm, u'citation style')
        cover.drawString(2.50*cm, pheight-21.5*cm, u'copyright')

        style = ParagraphStyle('citation style', fontName = 'Arial', \
            fontSize = 10, textColor = grey)
        language = self.request.get('language', '')
        P = Paragraph(self.context.get_citation_string(language), style)
        realwidth, realheight = P.wrap(pwidth-6.20*cm-2.5*cm, 10*cm)
        P.drawOn(cover, 6.20*cm, pheight-6.5*cm-realheight)

        copyright_txt = cover.beginText(6.20*cm, pheight-22.5*cm)
        copyright_txt.textLines(COPYRIGHT)
        cover.drawText(copyright_txt)

        cover.showPage()
        cover.save()
        return tmpfile

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """
        pdfdata = self._genCoverSheet()
        return pdfdata
