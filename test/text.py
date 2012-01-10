
from StringIO import StringIO
from nlmk.tokenizer import tokenize, sentences_index
from nlmk import stopwords
stopwords = stopwords()

from nlmk.text import sentence, iter_sentences, iter_tokens,\
                      iter_ngrams, collocations, frequency
from codecs import open

#fh = open("racin.txt", 'r', 'utf-8')
fh = open("nebeska.txt", 'r', 'utf-8')
content = fh.read()

fh.seek(0)

sent_idx = sentences_index(content)
del content

isents = iter_sentences(fh, sent_idx)

itokens = (t for t, s, tid in iter_tokens(isents))

ibig = iter_ngrams(itokens, n=2) 
#for s in    stopwords():
#    print s

#col = collocations(ibig)
#for l, r in col:
#    print ' '.join(r), l
fq =  frequency(itokens)
fq = ((t, c) for t, c in fq.iteritems() \
      if c>4 and t not in stopwords)
for t, c in sorted(fq, key=lambda item:-1*item[1]):
    print t,c

fh.close()
