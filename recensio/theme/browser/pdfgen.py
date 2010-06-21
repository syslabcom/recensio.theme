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
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

log = logging.getLogger('recensio.theme/pdfgen.py')

class GeneratePdfRecension(BrowserView):
    """View to generate PDF cover sheets
    """

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.copyright = u"This article may be downloaded and/or used within the private copying\nexemption. Any further use without permission of the rights shall be subject to\nlegal licences (§§ 44a-63a UrhG / German Copyright Act).\n\nDieser Beitrag kann vom Nutzer zu eigenen nicht-kommerziellen Zwecken\nheruntergeladen und/oder ausgedruckt werden. Darüber hinaus gehende\nNutzungen sind ohne weitere Genehmigung der Rechteinhaber nur im Rahmen\nder gesetzlichen Schrankenbestimmungen (§§ 44a-63a UrhG) zulässig."

        self.metadata_template = {
            "RezensioneinerMonographie": u"%(rezensionAutor)s, review of: %(authors)s, %(title)s%(titel_divider)s%(untertitel)s, \n%(erscheinungsort)s: %(verlag)s %(erscheinungsjahr)s, in: %(reihe)s \nBand %(reihennummer)s, p. %(seitenzahl)s, %(absolute_url)s",
            }

    def __call__(self):
        return self.genPdfRecension()

    def _prepareHeader(self, contentlength, filename='recension.pdf'):
        R = self.request.RESPONSE
        R.setHeader('content-type', 'application/pdf')
        R.setHeader('content-disposition', 'inline; filename="%s"' % filename)
        R.setHeader('content-length', str(contentlength))

    def _genCoverSheet(self):
        metadata_fields = map(lambda f: f.getName(), self.context.schema.getSchemataFields('default')) # [ 'rezensionAutor', 'autorDesBuchs', 'titel', 'untertitel', 'erscheinungsort', 'verlag', 'erscheinungsjahr', 'reihe', 'reihennummer', 'seitenzahl',  ]
        metadata_dict = dict()
        metadata_dict['seitenzahl'] = '123-456'
        for field in metadata_fields:
            log.debug('getting field %s' % field)
            metadata_dict[field] = self.context.getField(field).getAccessor(self.context)()
            if isinstance(metadata_dict[field], (tuple,list)):
                strval = ''
                for val in metadata_dict[field]:
                    strval += val + ', '
                metadata_dict[field] = strval[:-2]
            if metadata_dict[field] and not isinstance(metadata_dict[field], unicode):
                try:
                    metadata_dict[field] = metadata_dict[field].decode('utf8')
                except AttributeError:
                    log.warn('AttributeError while trying to decode %s (%s)' % (field, metadata_dict[field]))
        metadata_dict['titel_divider'] = u'. ' if metadata_dict['untertitel'] else u''
        metadata_dict['absolute_url'] = unicode(self.context.absolute_url())
        log.debug(metadata_dict)

        tmpfile,tmppath = tempfile.mkstemp(prefix='cover', suffix='.pdf')
        cover = canvas.Canvas(tmpfile, pagesize=A4)
        pwidth,pheight = A4
        cover.drawImage(os.path.join(os.path.split(os.path.abspath(__file__))[0], 
            'images/logo2_fuer-Deckblatt.jpg'), 0, pheight-4.21*cm, 
            width=28.28*cm, height=4.21*cm)
        cover.drawImage(os.path.join(os.path.split(os.path.abspath(__file__))[0], 
            'images/logo_icon_watermark.jpg'), pwidth/2.-.5*13.76*cm, pheight/2-.5*13.76*cm, 
            width=13.76*cm, height=13.76*cm, preserveAspectRatio=True, anchor='c')
        
        cover.setFont('Helvetica', 10)
        cover.setFillColor(grey)
        cover.drawString(2.50*cm, pheight-5.5*cm, u'citation style')
        cover.drawString(2.50*cm, pheight-21.5*cm, u'copyright')

        style = ParagraphStyle('citation style', fontName = 'Helvetica', fontSize = 10, textColor = grey)
        P = Paragraph(self.metadata_template[self.context.meta_type] % metadata_dict, style)
        P.wrap(pwidth-6.20*cm-2.5*cm, 10*cm)
        P.drawOn(cover, 6.20*cm, pheight-6.5*cm)

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
