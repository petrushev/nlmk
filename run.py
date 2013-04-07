# -*- coding: utf-8 -*-
from sys import argv
from os.path import dirname, abspath
from hashlib import md5
from struct import pack, unpack, calcsize
from collections import defaultdict
import json
from zlib import compress, decompress

from nlmk import text, tokenizer, tagger, corpus
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
        f.close()
    return sent_idx

def _cached_vocab(filepath):
    sig = _cache_sig(filepath)
    try:
        with open('%s/%s.vocab' % (_CACHE, sig), 'rb') as f:
            vocab_bin = f.read()
    except IOError:
        sent_idx = _cached_sentences_index(filepath)
        with open(filepath, 'r') as fh:
            lines = (line.decode('utf-8') for line in fh)
            vocab = text.vocabulary(text.iter_tokens(text.iter_sentences(lines, sent_idx)))
        vocab_bin = compress(json.dumps(vocab))
        with open('%s/%s.vocab' % (_CACHE, sig), 'wb') as f:
            f.write(vocab_bin)
    else:
        vocab = json.loads(decompress(vocab_bin))

    return vocab


def ngramgen(source, *cuttoff_info):
    """Generate n-grams with provided cuttoff"""

    try:
        fh = open(source, 'r')
    except Exception:
        print 'File not found:', source
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
    lines = (line.decode('utf-8') for line in fh)
    isents = text.iter_sentences(lines, sent_idx)

    itokens = (t for t, s, tid in text.iter_tokens(isents))
    res = ngramgenmod.multi_ngram(itokens, len(cuttoff_info))
    fh.close()

    res = ngramgenmod.cutt_ngrams(res, cuttoff_info)

    for dict_ in res:
        for tpl, v in dict_.iteritems():
            print (' '.join(tpl) + ' ' + unicode(v)).encode('utf-8')

def sentences(source, slice_ = None):
    """Fetch one or more sentences from a document"""
    try:
        fh = open(source, 'r')
    except Exception:
        print 'File not found:', source
        return

    sent_idx = _cached_sentences_index(source)
    total_sents = len(sent_idx) + 1

    if slice_ == None:
        l, r = 0, total_sents
    else:
        slice_ = [s.strip() for s in slice_.split(':')]
        if len(slice_) > 2:
            print 'Invalid slice:', ':'.join(slice_)
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
            l = int(slice_[0])
            r = min(l + 1, total_sents)
        else:
            l, r = 0, total_sents

    for i in range(l, r):
        print text.sentence(fh, i, sent_idx).encode('utf-8')

    fh.close()

def concordance(source, word, window = 4):
    """Concordance, finds word in a document along with context"""
    try:
        fh = open(source, 'r')
    except Exception:
        print 'File not found:', source
        return

    word = word.decode('utf-8')
    window = int(window)

    lines = (line.decode('utf-8') for line in fh)
    itokens = tokenizer.iter_tokenize(lines)
    for window in text.concordance(word, itokens, window):
        print ' '.join(window).encode('utf-8')
    fh.close()

def contexts(source, word):
    """Finds all contexts of a word"""
    try:
        fh = open(source, 'r')
    except Exception:
        print 'File not found:', source
        return

    fh.close()

    word = word.decode('utf-8')
    vocab = _cached_vocab(source)
    ctx = sorted(l + ' ' + r for l, r in text.contexts(word, vocab))
    for c in ctx: print c.encode('utf-8')

def _multi_iter_tokenize(sources):
    for source in sources:
        with open(source, 'r') as f:
            lines = (line.decode('utf-8') for line in f)
            itokens = tokenizer.iter_tokenize(lines)
            for t in itokens:
                yield t


def build_tagger(tagger_name, *sources):
    """Build a tagger given one or more documents"""
    sig = '%s/%s.tagger' % (_CACHE, tagger_name)
    ftager = open(sig, 'wb')
    itokens = _multi_iter_tokenize(sources)
    tagger_ = tagger.build_tagger(itokens)

    l, m, r = tagger_['L'], tagger_['M'], tagger_['R']

    list_tagger = [dict(('_'.join(key), values)
                         for key, values in T.iteritems())
                   for T in l, m, r]
    tagger_ = compress(json.dumps(list_tagger))
    ftager.write(tagger_)
    ftager.close()

def _load_tagger(tagger_name):
    sig = '%s/%s.tagger' % (_CACHE, tagger_name)
    with open(sig, 'rb') as f:
        list_tagger = json.loads(decompress(f.read()))
    tagger = {'L':defaultdict(tuple), 'M': defaultdict(tuple), 'R':defaultdict(tuple)}
    index_ = iter(['L', 'M', 'R'])
    for T in list_tagger:
        t_key = next(index_)
        for key, values in T.iteritems():
            key = tuple(str(key).split('_'))
            tagger[t_key][key] = tuple(map(str, values))

    return tagger

def tag(source, tagger_name):
    """Tag a document using a pre-built tagger"""
    tagger_ = _load_tagger(tagger_name)
    fh = open(source, 'r')
    lines = (line.decode('utf-8') for line in fh)
    itokens = tokenizer.iter_tokenize(lines)
    for token, tag in tagger.smart_tag(itokens, tagger_):
        tmp = token.encode('utf-8')
        if tag is not None:
            tmp = tmp + ' {{%s}}' % tag
        print tmp,
    fh.close()

def tf(source):
    """Term frequency distribution"""
    fh = open(source, 'r')
    lines = (line.decode('utf-8') for line in fh)
    itokens = tokenizer.iter_tokenize(lines)
    itokens = (token.lower() for token in itokens if token[0].isalpha())
    distribution = corpus.tf_distribution(itokens).items()
    distribution.sort(key = lambda item: -item[1])
    for token, val in distribution:
        print token.encode('utf-8'), '%.4f' % val

_runners = {'ngramgen': ngramgen, 'sentences': sentences, 'concordance': concordance,
            'contexts': contexts, 'build-tagger': build_tagger, 'tag': tag,
            'tf': tf}

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
    main()
