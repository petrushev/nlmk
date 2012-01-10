
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
    buf = u''
    sent_iter=iter(sent_idx)
    end = sent_iter.next()
    len_ = end
    for line in tx:  # read through file and do sentence segmentation
        buf = buf + line
        while len(buf)>=len_:  # buffer larger than wanted sentence -> sentence found!
            part = buf[:len_]  
            yield part.replace(u'\n',u' ').replace(u'\t',u' ').strip()  # yield sentence
            buf = buf[len_:]   # cutoff the buffer
            try:
                new_end = sent_iter.next()  # get the end and lenght of next sentence
                len_ = new_end - end
                end = new_end
            except StopIteration: # all sentences yielded, finish off the text
                buf = buf + tx.read()
                yield buf.replace(u'\n',u' ').replace(u'\t',u' ').strip() 
    
    
    
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
    
def frequency(tokens):
    tokens = sorted(t.lower() for t in tokens if len(t)>1)
    return dict((token, len(tuple(items))) for token, items in groupby(tokens))
