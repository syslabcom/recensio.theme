# vim:fileencoding=utf8
from cgi import escape
from pkg_resources import resource_filename
import logging
import os
import tempfile

from plone.uuid.interfaces import IUUID

from reportlab.lib.colors import grey
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from zope.i18n import translate

from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage

from recensio.contenttypes import contenttypesMessageFactory as _

log = logging.getLogger('recensio.theme/pdfgen.py')

COPYRIGHT = u"""This article may be downloaded and/or used within the
private copying exemption. Any further use without permission of the
rights shall be subject to legal licences (§§ 44a-63a UrhG / German
Copyright Act).

Dieser Beitrag kann vom Nutzer zu eigenen nicht-kommerziellen Zwecken
heruntergeladen und/oder ausgedruckt werden. Darüber hinaus gehende
Nutzungen sind ohne weitere Genehmigung der Rechteinhaber nur im
Rahmen der gesetzlichen Schrankenbestimmungen (§§ 44a-63a UrhG)
zulässig."""

class GeneratePdfRecension(BrowserView):
    """View to generate PDF cover sheets
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)

    def __call__(self):
        cover = new_path = None
        try:
            cover = self.genPdfRecension()
            pdf = self.context.get_review_pdf()
            error_code = None
            new_path = None
            if pdf:
                pdf_blob = pdf["blob"]
                original = pdf_blob.open().name
                fd, new_path = tempfile.mkstemp(prefix = 'final',
                                                suffix = '.pdf')
                os.close(fd) #2463
                error_code = os.system(
                    'ulimit -t 5;pdftk %s %s cat output %s' % (
                    cover, original, new_path
                    )
                    )
            if error_code or not pdf:
                IStatusMessage(self.request).add(
                    _(u'Creating the pdf has failed! Please try again '
                      'or ask for support'),
                    'error')
                return
            else:
                pdfdata = file(new_path).read()
        finally:
            if cover:
                os.remove(cover)
            if new_path:
                os.remove(new_path)

        self._prepareHeader(len(pdfdata), "%s.pdf" % IUUID(self.context))
        return pdfdata

    def _prepareHeader(self, contentlength, filename='review.pdf'):
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
        os.close(file_handle) #2463
        self.canvas = cover = canvas.Canvas(tmpfile, pagesize=A4)
        pwidth,pheight = A4

        language = self.request.get('language', '')
        # I want the syntax for translation look as similar as the real thing
        # But not similar enough for freaking out the translation string
        # extractors
        _X = lambda x: translate(x, target_language = language)
        # register the font (unicode-aware)
        font =  os.path.abspath(__file__ +\
                                '/../../data/DejaVuSerif.ttf')
        pdfmetrics.registerFont( TTFont('DejaVu-Serif', font) )

        self._drawImage('logo2_fuer-Deckblatt.jpg',
                        0,
                        pheight - 4.21*cm,
                        28.28*cm,
                        4.21*cm)

        pdf_watermark_path = resource_filename(
            __name__,
            os.path.join('images', 'logo_icon_watermark.jpg'))

        publication = self.context.get_parent_object_of_type("Publication")
        if publication != None:
            pdf_watermark_obj = getattr(publication, "pdf_watermark", None)
            if pdf_watermark_obj:
                pdf_watermark_path = pdf_watermark_obj.getBlob().open().name

        self.canvas.drawImage(
            pdf_watermark_path,
            6.2 * cm,
            9.5 * cm,
            6 * cm,
            6 * cm,
            preserveAspectRatio=True,
            anchor='sw',
            mask='auto' # To support transparent PNGs
            )
        cover.setFont('DejaVu-Serif', 10)
        cover.setFillColor(grey)
        citation = translate(_(u'label_citation_style',
                               default=u'citation style'),
                             target_language=language)
        cover.drawString(2.50*cm, pheight-5.5*cm, citation)
        cover.drawString(2.50*cm, pheight-21.5*cm, u'copyright')

        style = ParagraphStyle('citation style',
                               fontName = 'DejaVu-Serif',
                               fontSize = 10, textColor = grey)
        try:
            P = Paragraph(_(self.context.get_citation_string()), style)
        except UnicodeDecodeError:#ATF
            P = Paragraph(self.context.get_citation_string(), style)
        realwidth, realheight = P.wrap(pwidth-6.20*cm-2.5*cm, 10*cm)
        P.drawOn(cover, 6.20*cm, pheight-6.5*cm-realheight)
        # A small calculation, how much this paragaph would overlap
        # into the next paragraph. If the number is positive, we have
        # an overlap, and apply it to the initial offset
        overlap  = (pheight - 8.5 * cm) - (pheight - 6.5 * cm - realheight)
        overlap += 15 # padding

        if hasattr(self.context, 'getFirstPublicationData'):
            msgs = ['First published: ' + x
                    for x in self.context.getFirstPublicationData()]
            offset = max(overlap, 0)
            for msg in msgs:
                P2 = Paragraph(msg, style) # msg got escaped"
                realwidth, realheight = P2.wrap(pwidth-6.20*cm-2.5*cm, 10*cm)
                P2.drawOn(cover, 6.20*cm, pheight-8.5*cm-realheight - offset)
                offset += realheight

        P3 = Paragraph(_X(self.context.getLicense()), style)
        realwidth, realheight = P3.wrap(pwidth-6.20*cm-2.5*cm, 10*cm)
        P3.drawOn(cover, 6.20*cm, pheight-22.5*cm-realheight)

        cover.showPage()
        cover.save()
        return tmpfile

    def genPdfRecension(self):
        """Generate and return a PDF version of the recension
        """
        pdfdata = self._genCoverSheet()
        return pdfdata
