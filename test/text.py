# -*- coding: utf-8 -*-

from StringIO import StringIO
from time import time
from itertools import tee
from pprint import pprint

from nlmk.tokenizer import tokenize, sentences_index
from nlmk import stopwords, ra_unicode_read
stopwords = stopwords()

from nlmk.text import sentence, iter_sentences, iter_tokens,\
                      iter_ngrams, collocations, frequency, concordance,\
                      default_collocation_filter

from nlmk.tagger import iter_tagged, _base_tags, tag

from codecs import open

#fh = open("racin.txt", 'r', 'utf-8')
#fh = open("nebeska.txt", 'r', 'utf-8')
fh = open("lek_protiv_melanholijata.txt", 'r', 'utf-8')
content = fh.read()

#fh.seek(0)
#sent_idx = sentences_index(content)
#del content

#isents = iter_sentences(fh, sent_idx)

#itokens = (t for t, s, tid in iter_tokens(isents))

#ibig = iter_ngrams(itokens, n=2) 

def alpha_col_filter(word):
    return word > u'a' and word< u'џџ' and default_collocation_filter(word) 

#col = collocations(ibig, filter=alpha_col_filter)
#for l, r in col:
#    print l,r



#fq =  frequency(itokens)

#fq = ((t, c) for t, c in fq.iteritems() \
#      if c>4)
#for t, c in sorted(fq, key=lambda item:-1*item[1]):
#    print t

#content = ra_unicode_read(fh, 0, 15000)

tokens = tokenize(content)
itagged1 = ((token, _base_tags.get(tag(token),None)) for token in tokens)

itagged1, itagged2 = tee(itagged1)

all_ = 0
tagged = {}
for token, tag in itagged1:
    all_=all_+1
    if tag :
        tagged[tag]=tagged.get(tag,0)+1
#    if t.endswith(u'ам'):
#        print t

llx ={}
lxr ={}

for l,c,r in iter_ngrams(itagged2,3):
    (l, ltag), (c, ctag), (r, rtag)=l,c,r
    if ltag and ltag!='PU' and rtag and rtag!='PU'\
       and ctag and ctag!='PU':
        print l,c,r,'',ltag,ctag,rtag
        try:
            llx[(ltag,ctag)].add(rtag)
        except KeyError:
            llx[(ltag,ctag)]=set([rtag])
        try:
            lxr[(ltag,rtag)].add(ctag)
        except KeyError:
            lxr[(ltag,rtag)]=set([ctag])
              


print tagged
print sum(tagged.itervalues())*100/all_

pprint(llx)
pprint(lxr)
       

fh.close()
