## Script (Python) "listAuthors"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Returns a list of authors in the format "firstname lastname"
##
authors_list = []
for author in context.getAuthors():
    authors_list.append(u'%s %s' % (author['firstname'].decode('utf8'), author['lastname'].decode('utf8')))

return authors_list
