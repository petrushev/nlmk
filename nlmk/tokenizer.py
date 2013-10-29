# -*- coding: utf-8 -*-
from pyparsing import Word, Literal, originalTextFor, \
                      OneOrMore, nums, Or, Combine, alphas, \
                      oneOf

def someOf(*argv):
    return OneOrMore(Or(argv))


alpha_cap_uni = u"АБВГДЃЕЖЗЅИЈКЛЉМНЊОПРСТЌУФХЦЧЏШ"
alpha_lower_uni = u"абвгдѓежзѕијклљмнњопрстќуфхцчџшáèéѐôѝ"
alpha_uni = alpha_lower_uni + alpha_cap_uni

word = Word(alpha_uni)
latin_word = Word(alphas)
initial = Word(alpha_cap_uni, '.', exact = 2)

number = Word(nums)
bullet = originalTextFor(number + Literal('.'))
percent = originalTextFor(number + Literal('%'))

hypen_word = Combine(word + Literal('-') + word)
apos_word1 = Combine(Literal('\'') + word)
apos_word2 = Combine(word + Literal('\'') + word)

new_line = Literal('\n')
tab = Literal('\t')
punctuation = list(u"‘’.,;„“”()‘:\"\'`′!?-–—…") + ['...']
punkt = map(Literal, punctuation)

all_ = [word, initial, bullet, hypen_word, apos_word1, apos_word2, \
          number, percent, new_line, latin_word, tab]
all_.extend(punkt)
all_ = Or(all_).parseWithTabs()


def tokenize(feed, include_junk = True, echo_junk = False):
    """Returns list of tokens"""
    tokens = []
    start = 0
    for t, s, e in all_.scanString(feed):
        if s != 0:
            junk = feed[start:s].strip()
            if junk != "":
                if include_junk: tokens.append(junk)
                if echo_junk: print junk
        if t[0]:
            tokens.append(t[0])
        start = e

    junk = feed[start:].strip()
    if junk != "":
        if include_junk: tokens.append(junk)
        if echo_junk: print junk

    return tokens

def _tokenize(feed):
    start = 0
    for t, s, e in all_.scanString(feed):
        if s != 0:
            junk = feed[start:s].strip()
            if junk != "": yield junk
        if t[0]: yield t[0]
        start = e

    junk = feed[start:].strip()
    if junk != "": yield junk

def iter_tokenize(tx, include_junk = True, echo_junk = False):
    """Iterate through tokens using filelike object as feed (memory efficient)"""
    for line in tx:
        for token in _tokenize(line):
            yield token

def sentences_index(feed):
    """Returns list of sentence beginings starting from second sentence"""
    #start = oneOf(list(u'.?!…')) | Literal('...')
    start = Or(map(Literal, list(u'.?!…') + ['...', u'.”', u'”.', u'”.', u'".' ]))

    end = oneOf(list(u'\n' + u'-—"„“”' + alpha_cap_uni))
    parser = start + end
    parser = parser.parseWithTabs()
    return [item[1] + len(item[0]) for item in parser.scanString(feed)]
