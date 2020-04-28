## Script (Python) "getAvailValues"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=voctype
##title=Returns available values for ddcPlace
##
outlines = []
for line in context.portal_vocabularies.getVocabularyByName(
    voctype
).getVocabularyLines():
    voclbl = line[1][0]
    vocval = line[0]
    outlines.append(dict(label=voclbl, value=vocval))
    for subline in line[1][1].items():
        subvoclbl = subline[1][0]
        subvocval = subline[0]
        outlines.append(dict(label="%s - %s" % (voclbl, subvoclbl), value=subvocval))

return outlines
