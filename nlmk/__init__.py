from functools import reduce
from operator import add

def ra_unicode_read(fh, start, end):
    """Read random-access file on positions given as unicode string"""
    tmp_pos = fh.tell()
    fh.seek(0)

    buf = u""
    iter_fh = (line.decode('utf-8') for line in fh)

    for line in iter_fh:
        line_len = len(line)
        # .. recalibrate start/end ...
        if line_len < start:
            start = start - line_len
            if end is not None:
                end = end - line_len
        else:
            # ...until start is met
            buf = buf + line

            # cutoff start
            buf = buf[start:]
            if end is not None:
                end = end - start

            break

    if end is not None:
        # read enough lines so the end is met
        while len(buf) < end:
            try:
                buf = buf + iter_fh.next()
            except StopIteration:
                # end-of-file: end will not be met
                break
        buf = buf[:end]

    fh.seek(tmp_pos)   # restore the file position

    return buf


def stopwords():
    from nlmk._stopwords import _stopwords
    return _stopwords
