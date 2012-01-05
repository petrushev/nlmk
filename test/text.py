
from StringIO import StringIO
from nlmk.tokenizer import tokenize, sentences_index
from nlmk import stopwords

from nlmk.text import sentence, iter_sentences, iter_tokens, iter_ngrams,\
    collocations
from codecs import open , EncodedFile

fh = open("racin.txt", 'r', 'utf-8')
content = fh.read()

fh.seek(0)

sent_idx = sentences_index(content)
del content

isents = iter_sentences(fh, sent_idx)

itokens = (t for t, s, tid in iter_tokens(isents))

ibig = iter_ngrams(itokens, n=2) 
#for s in    stopwords():
#    print s

col = collocations(ibig)
for l, r in col:
    print ' '.join(r), l

fh.close()
