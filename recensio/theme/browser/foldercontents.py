from Acquisition import aq_inner
from plone.app.content.browser.tableview import Table
from plone.app.content.browser.foldercontents import FolderContentsTable
from plone.app.content.browser.foldercontents import FolderContentsView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.interface import IATTopic

class ICTTable(Table):
    """ """
    render = ViewPageTemplateFile("templates/table.pt")

class ICTFolderContentsTable(FolderContentsTable):
    """ """

    def __init__(self, context, request, contentFilter={}):
        super(ICTFolderContentsTable, self).__init__(context, request, contentFilter)
        url = context.absolute_url()
        view_url = url + '/@@folder_contents'
        self.table = ICTTable(
                            request, url, view_url, self.items,
                            show_sort_column=self.show_sort_column,
                            buttons=self.buttons, )
                       
    def getFilteredFolderContents(self,contentFilter=None,batch=False,b_size=100,full_objects=False):
        """ wrapper method around to use catalog to get folder contents 
            extends getFolderContents and does not display folders which have excludeFromNav==False """
            
        context = self.context
        mtool = context.portal_membership
        cur_path = '/'.join(context.getPhysicalPath())
        path = {}

        if not contentFilter:
            contentFilter = {}
        else:
            contentFilter = dict(contentFilter)

        if not contentFilter.get('sort_on', None):
            contentFilter['sort_on'] = 'getObjPositionInParent'

        if contentFilter.get('path', None) is None:
            path['query'] = cur_path
            path['depth'] = 1
            contentFilter['path'] = path

        show_inactive = mtool.checkPermission('Access inactive portal content', context)

        # Evaluate in catalog context because some containers override queryCatalog
        # with their own unrelated method (Topics)
        contents = context.portal_catalog.queryCatalog(contentFilter, show_all=1,
                                                          show_inactive=show_inactive)

        # filter out folders appearing in the navigation
        filteredlist = []
        metaTypesNotToList = context.portal_properties.navtree_properties.getProperty('metaTypesNotToList')
        
        for b in contents: 
            if not hasattr(b, 'exclude_from_nav') or not hasattr(b, 'is_folderish'):
                # fallback for objects not having the attrs
                filteredlist.append(b)
                continue

            if b.exclude_from_nav==True or b.portal_type in metaTypesNotToList: # or b.review_state == 'private':
                filteredlist.append(b)

        contents = filteredlist

        if full_objects:
            contents = [b.getObject() for b in contents]

        if batch:
            from Products.CMFPlone import Batch
            b_start = context.REQUEST.get('b_start', 0)
            batch = Batch(contents, b_size, int(b_start), orphan=0)
            return batch

        return contents
        
    def contentsMethod(self):
        context = aq_inner(self.context)
        if IATTopic.providedBy(context):
            contentsMethod = context.queryCatalog
        else:
            contentsMethod = self.getFilteredFolderContents
        return contentsMethod
        

class ICTFolderContentsView(FolderContentsView):
    """ """

    def __init__(self, context, request):
        super(ICTFolderContentsView, self).__init__(context, request)

    def contents_table(self):
        table = ICTFolderContentsTable(aq_inner(self.context), self.request)
        return table.render()

