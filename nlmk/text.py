
from itertools import groupby

from nlmk import ra_unicode_read
from nlmk.tokenizer import tokenize

from nlmk import stopwords
stopwords = stopwords()

def sentence(tx, i, sent_idx):
    """Returns i-th sentence from tx (file-like text feed), given sentence index"""
    if i > len(sent_idx):
        raise IndexError, "Text has %d sentences, wanted %d"\
                          % (len(sent_idx)+1, i+1 )
    
    if i==0:
        sent = ra_unicode_read(tx, 0, sent_idx[0])
    elif i==len(sent_idx):
        sent = ra_unicode_read(tx, sent_idx[-1], None)
    else:
        sent = ra_unicode_read(tx, sent_idx[i-1], sent_idx[i])
    
    return sent.replace(u'\n',u' ').replace(u'\t',u' ').strip()
    
    
def iter_sentences(tx, sent_idx):
    tx.seek(0)
    start = 0
    for end in sent_idx:        
        sent = reduce(unicode.__add__, (tx.read(1) for i in xrange(start, end)), u'')
        sent = sent.replace(u'\n',u' ').replace(u'\t',u' ').strip()
        start = end
        yield sent
        
    ending= tx.read().replace(u'\n',u' ').replace(u'\t',u' ').strip()
    tx.seek(0)
    yield ending
    
    
def iter_tokens(sentences):
    """Returns iterator of triplets: token, sentence_id, token_id """ 
    for sent_id, sent in enumerate(sentences):
        tokens = tokenize(sent)
        for token_id, token in enumerate(tokens):
            yield token, sent_id, token_id
            
def iter_ngrams(tokens, n=2):
    """Returns iterator of ngrams for a sequence of tokens"""
    history = []
    for token in tokens:
        history.append(token)
        if len(history)==n:
            ngram = tuple(history)
            history.pop(0)
            yield ngram
            
def default_collocation_filter(token):
    return len(token)>2 and token not in stopwords
            
def collocations(bigrams, filter=default_collocation_filter):
    collocs = ((l.lower(), r.lower()) for l, r in bigrams)
    collocs = sorted(  (l, r) for l, r in collocs \
                       if filter(l) and filter(r)   )
    collocs = sorted(  ( (len(list(items)), colloc) \
                        for colloc, items in groupby(collocs)),
                     reverse=True)
    
    return collocs
    
    
    
