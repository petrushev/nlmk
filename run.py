from sys import argv
from os.path import dirname, abspath
import codecs
from hashlib import md5
from struct import pack, unpack, calcsize

from nlmk import text
from nlmk import tokenizer
from nlmk import ngramgen as ngramgenmod

_CACHE = abspath(dirname(__file__)) + '/.cache'

def _cache_sig(filepath):
    return md5(abspath(filepath)).hexdigest()

def _cached_sentences_index(filepath):
    sig = _cache_sig(filepath)
    cache = '%s/%s.sentidx' % (_CACHE, sig)

    try:
        f = open(cache, 'rb')
    except IOError:
        with open(filepath, 'r') as f:
            content = f.read()
            sent_idx = tokenizer.sentences_index(content.decode('utf-8'))
        with open(cache, 'wb') as f:
            for i in sent_idx:
                f.write(pack('I', i))
    else:
        size = calcsize('I')
        sent_idx = []
        while True:
            buf = f.read(size)
            if len(buf) < size: break
            sent_idx.append(unpack('I', buf)[0])
    return sent_idx


def ngramgen(source, *cuttoff_info):
    """Generate n-grams with provided cuttoff"""

    try:
        fh = codecs.open(source, 'r', 'utf-8')
    except Exception:
        print 'File not found or invalid utf-8:', source
        return

    try:
        cuttoff_info = map(int, cuttoff_info)
    except ValueError:
        print 'Invalid cuttoff info provided, list of integers needed'
        return

    if len(cuttoff_info) == 0:
        print 'Cuttoff info provided is zero length'
        return

    sent_idx = _cached_sentences_index(source)

    fh.seek(0)
    isents = text.iter_sentences(fh, sent_idx)

    itokens = (t for t, s, tid in text.iter_tokens(isents))
    res = ngramgenmod.multi_ngram(itokens, len(cuttoff_info))
    fh.close()

    res = ngramgenmod.cutt_ngrams(res, cuttoff_info)

    for dict_ in res:
        for tpl, v in dict_.iteritems():
            print (' '.join(tpl) + ' ' + unicode(v)).encode('utf-8')

def sentences(source, slice_ = None):
    try:
        fh = codecs.open(source, 'r', 'utf-8')
    except Exception:
        print 'File not found or invalid utf-8:', source
        return

    sent_idx = _cached_sentences_index(source)
    total_sents = len(sent_idx) + 1

    if slice_ == None:
        l, r = 0, total_sents
    else:
        slice_ = [s.strip() for s in slice_.split(':')]
        if len(slice_) > 2:
            print 'Invalid slice:', ':'.join(slice)
            return
        if len(slice_) == 2:
            l, r = slice_
            if l == '' and r == '':
                l, r = 0, total_sents
            elif l == '':
                l = 0
                r = min(int(r), total_sents)
            elif r == '':
                l = int(l)
                r = total_sents
            else:
                l, r = int(l), min(int(r), total_sents)
        elif len(slice_) == 1:
            l = int(slice[0])
            r = min(l + 1, total_sents)
        else:
            l, r = 0, total_sents

    for i in range(l, r):
        print text.sentence(fh, i, sent_idx)

_runners = {'ngramgen': ngramgen, 'sentences': sentences}

def main():
    try:
        case = argv[1]
    except IndexError:
        print('No runner provided.')
        return

    if case == 'main': return

    try:
        case = _runners[case]
    except KeyError:
        print 'Runner %s not found.\nAvailable runners:' % case
        for runner, runner_fc in _runners.iteritems():
            print '    %s: %s' % (runner, runner_fc.__doc__)
        return

    args = argv[2:]
    case(*args)


if __name__ == '__main__':
    #print _cached_sentences_index('corpus/racin.txt')
    main()