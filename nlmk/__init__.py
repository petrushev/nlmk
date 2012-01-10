
from functools import reduce
from operator import add

def ra_unicode_read(fh, start, end):
    """Read random-access file on positions given as unicode string"""
    tmp_pos = fh.tell()
    fh.seek(0)
    
    buf = u""
    iter_fh = iter(fh)
    for line in iter_fh:  # read file line-by-line...
        line_len = len(line)
        if line_len<start:        # .. recalibrate start/end ...   
            start=start-line_len
            end=end-line_len
        else:                     # ...until start is met
            buf = buf + line
            buf=buf[start:]       # cutoff start
            end=end-start
            break
    while len(buf)<end:             # read enough lines so the end is met
        buf = buf + iter_fh.next()
    buf = buf[:end]
    
    fh.seek(tmp_pos)   # restore the file position
    return buf


def stopwords():
    from nlmk._stopwords import _stopwords
    return _stopwords
        