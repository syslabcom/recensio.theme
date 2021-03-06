## Script (Python) "Display Value"
##title=Use DisplayList getValue method to translate internal value to a label
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=vocab, value, widget=None


try:
    # Maybe a string?
    value.capitalize()
except AttributeError:
    try:
        # Maybe a list?
        return ", ".join(
            [
                vocab.getValue(context.unicodeEncode(v), "")
                for v in value
                if v and vocab.getValue(context.unicodeEncode(v), False)
            ]
        )
    except TypeError:
        pass

# Try to convert to a string and do the dirty job.
return vocab.getValue(context.unicodeEncode(value), "")
