# -*- coding: utf-8 -*-

from codecs import open
from pprint import pprint
from operator import itemgetter

from nlmk.tokenizer import sentences_index, punctuation
from nlmk.text import iter_sentences, iter_tokens  

DICTPATH = '/home/petrushev/Desktop/dict.dat'

grammars = u"ж|м|несв|прид|св. и несв|ср|прил|изв|преф|само мн|скр|св|чест|мод|име|сврз||зам|сло|бр|предл|суф|пнкт|нум".split(u"|")
PUNKT = len(grammars)-2
NUM = len(grammars)-1

def load_dict(dictpath):
    glos = {}
    
    with open(DICTPATH, 'r','utf-8') as f:
        for line in f:
            lexem, gr = line.strip().split(u'|')
            gr_id = grammars.index(gr)
                
            if len(lexem)<2: continue
            beg, rest = lexem[:2], lexem[2:]
            
            try:
                glos[beg][rest]=gr_id
            except KeyError:
                glos[beg]={rest:gr_id}

    return glos

def get_grammar(lexem, glossary):
    if lexem in punctuation:
        return PUNKT
    if lexem.isdigit():
        return NUM
    beg, rest = lexem[:2], lexem[2:]
    try: return glossary[beg][rest]
    except KeyError:
        if beg.islower(): return None
        beg = beg.lower()
        try: return glossary[beg][rest]
        except KeyError: 
            return None
        
glossary = load_dict(DICTPATH)

fh = open("racin.txt", 'r', 'utf-8')
#fh = open("nebeska.txt", 'r', 'utf-8')
#fh = open("lek_protiv_melanholijata.txt", 'r', 'utf-8')
content = fh.read()

fh.seek(0)
sent_idx = sentences_index(content)
del content

isents = iter_sentences(fh, sent_idx)
itokens = (t for t, s, tid in iter_tokens(isents))
for t in itokens:
    tag= get_grammar(t, glossary)
    if tag is None:
        print t
    




fh.close()