import logging


log = logging.getLogger(__name__)


def reindex_on_reorder(obj, evt):
    """Quick fix: for some reason objects are not reindexed properly after
    reordering. Needed for FLOW-229
    """
    for child in obj.objectValues():
        try:
            child.reindexObject()
        except Exception:
            log.info("Not reindexing {}".format(child.getId()))
