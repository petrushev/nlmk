# -*- coding: utf-8 -*-

from StringIO import StringIO
from time import time

from nlmk.tokenizer import tokenize, sentences_index
from nlmk import stopwords, ra_unicode_read
stopwords = stopwords()

from nlmk.text import sentence, iter_sentences, iter_tokens,\
                      iter_ngrams, collocations, frequency, concordance,\
                      default_collocation_filter
from codecs import open

#fh = open("racin.txt", 'r', 'utf-8')
#fh = open("nebeska.txt", 'r', 'utf-8')
fh = open("lek_protiv_melanholijata.txt", 'r', 'utf-8')
content = fh.read()
fh.seek(0)

sent_idx = sentences_index(content)
del content

isents = iter_sentences(fh, sent_idx)

itokens = (t for t, s, tid in iter_tokens(isents))

ibig = iter_ngrams(itokens, n=2) 

def alpha_col_filter(word):
    return word > u'a' and word< u'џџ' and default_collocation_filter(word) 

#col = collocations(ibig, filter=alpha_col_filter)
#for l, r in col:
#    print l,r



fq =  frequency(itokens)

fq = ((t, c) for t, c in fq.iteritems() \
      if c>4)
for t, c in sorted(fq, key=lambda item:-1*item[1]):
    print t

fh.close()
