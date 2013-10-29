from itertools import groupby, tee
from operator import itemgetter

from nlmk import ra_unicode_read
from nlmk.tokenizer import tokenize
from nlmk import stopwords
stopwords = stopwords()

key0 = itemgetter(0)

def sentence(tx, i, sent_idx):
    """Returns i-th sentence from tx (file-like text feed), given sentence index"""
    if i > len(sent_idx):
        raise IndexError, "Text has %d sentences, wanted %d"\
                          % (len(sent_idx) + 1, i + 1)

    if i == 0:
        sent = ra_unicode_read(tx, 0, sent_idx[0])
    elif i == len(sent_idx):
        sent = ra_unicode_read(tx, sent_idx[-1], None)
    else:
        sent = ra_unicode_read(tx, sent_idx[i - 1], sent_idx[i])

    return sent.replace(u'\n', u' ').replace(u'\t', u' ').strip()


def iter_sentences(tx, sent_idx):
    """Iterates through sentences of a text previously segmented"""
    buf = u''
    sent_iter = iter(sent_idx)
    end = sent_iter.next()
    len_ = end
    for line in tx:  # read through file and do sentence segmentation
        buf = buf + line
        while len(buf) >= len_:  # buffer larger than wanted sentence -> sentence found!
            part = buf[:len_]
            yield part.replace(u'\n', u' ').replace(u'\t', u' ').strip()  # yield sentence
            buf = buf[len_:]   # cutoff the buffer
            try:
                new_end = sent_iter.next()  # get the end and lenght of next sentence
                len_ = new_end - end
                end = new_end
            except StopIteration: # all sentences yielded, finish off the text
                yield buf.replace(u'\n', u' ').replace(u'\t', u' ').strip()

def iter_tokens(sentences):
    """Returns iterator of triplets: token, sentence_id, token_id """
    for sent_id, sent in enumerate(sentences):
        tokens = tokenize(sent)
        for token_id, token in enumerate(tokens):
            yield token, sent_id, token_id

def iter_ngrams(tokens, n = 2):
    """Returns iterator of ngrams for a sequence of tokens"""
    history = []
    for token in tokens:
        history.append(token)
        if len(history) == n:
            ngram = tuple(history)
            history.pop(0)
            yield ngram


def default_collocation_filter(token):
    """For use in `collocations`, drops letters, punctuation and stopwords"""
    return len(token) > 2 and token not in stopwords


def collocations(bigrams, filter = default_collocation_filter):
    """Returns sorted list of common bigrams"""
    # lower and filter
    collocs = ((l.lower(), r.lower()) for l, r in bigrams)
    collocs = sorted((l, r) for l, r in collocs \
                       if filter(l) and filter(r))
    # count and sort
    collocs = sorted(((len(list(items)), colloc) \
                         for colloc, items in groupby(collocs)),
                     key = key0)

    total_collocs = sum(item[0] for item in collocs)

    # group by freq
    threshold_percent = 0
    for cnt, items in groupby(collocs, key = key0):
        len_ = len(list(items))
        threshold_percent = threshold_percent + cnt * len_ * 1.0 / total_collocs
        if threshold_percent < 0.97:   # rise threshold
            threshold = cnt
        if threshold_percent > 0.3:  # enough cutting
            break

    if threshold == 0: threshold = 1  # cut simple bigrams anyway

    return sorted(item for cnt, item in collocs if cnt > threshold)


def frequency(tokens, no_stopwords = True):
    """Return dictionary of frequencies per token,
    exclude stopwords by default"""
    tokens = sorted(t.lower() for t in tokens
                    if len(token) > 1 and (not no_stopwords or (token.lower() not in stopwords)))
    tokens.sort()
    return dict((token, len(tuple(items))) \
                 for token, items in groupby(tokens))

def concordance(word, tokens, window = 4):
    """Goes through a tokens sequence to find 
    occurences of a word and iterates it in a window"""
    word = word.lower()
    for window_tokens in iter_ngrams(tokens, window * 2 + 1):
        # the word is in the middle of window
        if window_tokens[window].lower() == word:
            yield window_tokens

def vocabulary(token_triplets):
    """Vocabulary, each word contains list of pairs (sent_id, token_id)"""
    vocab = {}
    for token, sent_id, token_id in token_triplets:
        if len(token) == 1: continue
        token = token.lower()
        pair = (sent_id, token_id)
        try:
            vocab[token].append(pair)
        except KeyError:
            vocab[token] = [pair]

    return vocab

def _vocabulary_idx_look(vocabulary, sent_id, token_id):
    """Reverse lookup in a vocabulary, returns word at index: `sent_id`, `token_id`"""
    for word, positions in vocabulary.iteritems():
        for sent_id_, token_id_ in positions:
            if sent_id_ == sent_id and token_id_ == token_id:
                return word
    raise IndexError, 'position not in vocabulary'


def contexts(word, vocabulary):
    """Iterate contexts for a given word"""
    word = word.lower()
    positions = vocabulary.get(word, [])
    wrappers = set()
    for sent_id, token_id in positions:
        if token_id == 0: continue # beginning of sentence
        try:
            l = _vocabulary_idx_look(vocabulary, sent_id, token_id - 1)
            r = _vocabulary_idx_look(vocabulary, sent_id, token_id + 1)
        except IndexError:
            pass
        else:
            wrappers.add((l, r))
    return wrappers

# TODO : broken
"""Find words in similar contexts"""
"""

def similar(word, tokens):
    word = word.lower()
    it1, it2 = tee(iter(tokens)) #copy iterators
    contexts_ = contexts(word, it1)
    sims = set([])
    for item in iter_ngrams(it2, 3):
        item = [i.lower() for i in item]
        if item[1] == word: continue
        if any([len(t) < 2 for t in item]): continue  # punctuation
        for l, r in contexts_:
            if l == item[0] and r == item[2]:
                sims.add(item[1])

    return sims

"""
