def reindex_on_reorder(obj, evt):
    """ Quick fix: for some reason objects are not reindexed properly after
    reordering. Needed for FLOW-229
    """
    for child in obj.objectValues():
        child.reindexObject()
