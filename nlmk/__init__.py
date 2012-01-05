
from functools import reduce

def ra_unicode_read(fh, start, end):
    """Read random-access file on positions given as unicode string"""
    tmp_pos = fh.tell()
    fh.seek(0)
    for i in xrange(start): fh.read(1)
    if end is None:
        content = fh.read()
    else:
        content = reduce(unicode.__add__, (fh.read(1) for i in xrange(start, end)), u'') 
    fh.seek(tmp_pos)
    return content


def stopwords():
    from nlmk._stopwords import _stopwords
    return _stopwords
        