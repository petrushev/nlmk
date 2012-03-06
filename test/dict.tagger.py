# -*- coding: utf-8 -*-

from codecs import open
from pprint import pprint
from operator import itemgetter
from struct import pack, unpack, calcsize

from nlmk.tokenizer import sentences_index, punctuation
from nlmk.text import iter_sentences, iter_tokens , iter_ngrams 

DICTPATH = '/home/petrushev/Desktop/dict.dat'

grammars = u"ж|м|несв|прид|св. и несв|ср|прил|изв|преф|само мн|скр|св|чест|мод|име|сврз||зам|сло|бр|предл|суф".split(u"|")

grammars = {u"ж": 0 ,
            u"м": 0 ,
            u"несв": 1 ,
            u"прид": 2 ,
            u"св. и несв": 1 ,
            u"ср": 0 ,
            u"прил": 3 ,
            u"изв": 4 ,
            u"преф": None ,
            u"само мн": 0 ,
            u"скр": None ,
            u"св": 1 ,
            u"чест": 6 ,
            u"мод": 10  ,
            u"име": 0 ,
            u"сврз": 5 ,
            u"": None ,
            u"зам": 7 ,
            u"сло": 0 ,
            u"бр": 8 ,
            u"предл": 9 ,
            u"суф": None  }

reverse_grammar = {0:'N', 1:'V', 2:'ADJ', 3:'ADV', 4:'ITJ',
                   5:'CNJ', 6:'PRT', 7:'PRO', 8:'NUM', 9:'PRP', 10:'MOD' }

def load_dict(dictpath):
    glos = {}
    
    with open(DICTPATH, 'r','utf-8') as f:
        for line in f:
            lexem, gr = line.strip().split(u'|')
            gr_id = grammars[gr]
                
            if len(lexem) < 2:
                beg, rest = '', lexem
            else:
                beg, rest = lexem[:2], lexem[2:]
                
            try:
                glos[beg][rest]=gr_id
            except KeyError:
                glos[beg]={rest:gr_id}

    return glos

def get_grammar(lexem, glossary):
    #if lexem in punctuation:
    #    return PUNKT
    if lexem.isdigit():
        return 8
    if len(lexem) < 2:
        beg, rest = '' , lexem
    else:
        beg, rest = lexem[:2], lexem[2:]
        
    try: return glossary[beg][rest]
    except KeyError:
        if beg.islower(): return None
        beg = beg.lower()
        try: return glossary[beg][rest]
        except KeyError: 
            return None
        
glossary = load_dict(DICTPATH)

#fh = open("racin.txt", 'r', 'utf-8')
fh = open("nebeska.txt", 'r', 'utf-8')
"""
#fh = open("lek_protiv_melanholijata.txt", 'r', 'utf-8')
content = fh.read()

fh.seek(0)
sent_idx = sentences_index(content)
del content

isents = iter_sentences(fh, sent_idx)
itokens = (t for t, s, tid in iter_tokens(isents))

with open('/home/petrushev/Desktop/nebeska.tag.bin', 'wb') as bin:
    for token in itokens:
        tag = get_grammar(token, glossary)
        if tag is None:
            bin.write(pack('I',99))
        else:
            bin.write(pack('I',tag))


"""
bin = open('/home/petrushev/Desktop/nebeska.tag.bin', 'rb')
sz = calcsize('I')

#itokenized = [(token, reverse_grammar.get( unpack('I',bin.read(sz))[0] , None)) \
#              for token_id, token in enumerate(itokens) ]
tags = []
while True:
    buf = bin.read(sz)
    if len(buf)!=sz: break
    tags.append( reverse_grammar.get(unpack('I', buf)[0], None) )

trained = {}

for (lt, ct , rt) in iter_ngrams(tags, 3):
    if lt and ct and rt:
        try:
            trained[(lt, ct, rt)]+=1
        except KeyError:
            trained[(lt, ct, rt)]=1

bin.close()

for lt, ct, rt in trained.keys():
    print lt, ct, rt, trained[(lt, ct, rt)]



fh.close()