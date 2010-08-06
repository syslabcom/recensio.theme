## Script (Python) "listAuthors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=listEditors=False
##title=Returns a list of authors in the format "firstname lastname"
##
if not getattr(context, 'getAuthors', None):
    return None
authors_list = []
for author in context.getAuthors():
    authors_list.append(u'%s %s' % (author['firstname'].decode('utf8'), author['lastname'].decode('utf8')))
if listEditors:
    if not getattr(context, 'getEditorsCollectedEdition', None):
        return authors_list
    for editor in context.getEditorsCollectedEdition():
        authors_list.append(u'%s %s' % (editor['firstname'].decode('utf8'), editor['lastname'].decode('utf8')))

return authors_list
