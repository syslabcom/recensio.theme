import logging
log = logging.getLogger('recensio.theme/util.py')

citation_templates = {
    "Review einer Monographie": u"%(reviewAuthor)s, review of: %(authors)s, %(title)s%(titel_divider)s%(subtitle)s, %(placeOfPublication)s: %(publisher)s %(yearOfPublication)s, in: %(series)s, %(seriesVol)s, p. %(pages)s, %(absolute_url)s",
    "Presentation Article Review": u"%(reviewAuthor)s, review of: %(shortnameJournal)s, %(volume)s, %(number)s, (%(yearOfPublication)s/%(officialYearOfPublication)s, %(absolute_url)s",
    "Praesentationen von Monographien": u"%(authors)s, presentation of: %(authors)s, %(title)s%(titel_divider)s%(subtitle)s, %(placeOfPublication)s: %(publisher)s %(yearOfPublication)s, %(absolute_url)s",
    }


def getCitationString(review):
    metadata_fields = map(lambda f: f.getName(), review.schema.getSchemataFields('default')) # [ 'reviewAuthor', 'autorDesBuchs', 'titel', 'subtitle', 'placeOfPublication', 'publisher', 'yearOfPublication', 'series', 'seriesVol', 'pages',  ]
    metadata_dict = dict()
    metadata_dict['pages'] = '123-456'
    for field in metadata_fields:
        log.debug('getting field %s' % field)
        metadata_dict[field] = review.getField(field).getAccessor(review)()
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
    metadata_dict['titel_divider'] = u'. ' if metadata_dict['subtitle'] else u''
    metadata_dict['absolute_url'] = unicode(review.absolute_url())
    log.debug(metadata_dict)
    return citation_templates[review.portal_type] % metadata_dict
