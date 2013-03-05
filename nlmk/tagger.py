# -*- coding: utf-8 -*-
from collections import defaultdict
from operator import or_, itemgetter
from itertools import tee

from nlmk.text import iter_ngrams

_ext = {
  u'јќи':'GP', # глаголски прилог
  u'ува':'NSV', # несвојствен глагол
  u'увал':'NSVL', # несвојствен глагол, л-форма
  u'увала':'NSVL',
  u'увале':'NSVL',
  u'увало':'NSVL',
  u'дил':'GL', # глагол, л-форма
  u'дила':'GL', # глагол, л-форма
  u'диле':'GL', # глагол, л-форма
  u'дило':'GL', # глагол, л-форма
  u'ше':'NSV',
  u'аат':'GP3', # глагол, плурал, 3лице,
  u'ениот':'PRMC',   # придавка, машки род, член
  u'чните':'PRPC',  # придавка, плурал, множина
  u'чни':'PRP', # придавка, плурал
  u'ици':'IP', # именка, плурал
  u'иците':'IPC', # именка, плурал, член
  u'ник':'IM', # именка, машки род
  u'никот':'IMC', # именка, машки род, член
  u'отот':'IMC',
  u'онот':'IMC',
  u'риот':'PR',  # придавка
  u'рата':'PR',  # придавка
  u'рите':'PR',  # придавка
  u'ање':'GI',    # глаголска именка
  u'дачи':'IM',
  u'цачи':'IM',
  u'ција':'IF',     # именка женски род
  u'цијата':'IFC', # именка женски род, член
  u'ината':'IFC', # именка женски род, член
  u'ции':'IFP',     # именка женски род, множина
  u'циите':'IFPC'   # именка женски род, множина, член

  #u'ици':'I' # именка
}

_exact = {
  'PU':list(u',.[]()"„“`\';:!?-—'),
  'PR':[u'мој', u'мои', u'моја', u'мое', u'мојот', u'мојата', u'моето', u'моите',
        u'твој', u'твои', u'твоја', u'твое', u'твојот', u'твоите', u'твојата', u'твоето',
        u'негов', u'негова', u'негово', u'негови', u'неговиот', u'неговата', u'неговото', u'неговите',
        u'нејзин', u'нејзина', u'нејзино', u'нејзини', u'нејзиниот', u'нејзината', u'нејзиното', u'нејзините',
        u'наш', u'наша', u'наше', u'наши', u'нашиот', u'нашата', u'нашето', u'нашите',
        u'ваш', u'ваше', u'веша', u'ваши', u'вашиот', u'вашето', u'вешата', u'вашите',
        u'нивен', u'нивна', u'нивно', u'нивни', u'нивниот', u'нивната', u'нивното', u'нивните',
        u'свој', u'своја', u'свое', u'свои', u'својот', u'својата', u'своето', u'своите'],
  'Z':[u'сам', u'сама', u'само', u'сами', u'самиот', u'самата', u'самото', u'самите',
       u'мене', u'ме', u'ми', u'тебе', u'те', u'ти', u'нему', u'му', u'него', u'го', u'нејзе', u'ѝ', u'неа', u'ја',
       u'нас', u'не', u'нам', u'ни', u'вас', u'ве', u'вам', u'ви', u'ним', u'им', u'нив', u'ги',
       u'себе', u'си',
       u'кој', u'која', u'кое', u'кои', u'чиј', u'чија', u'чие', u'чии',
       u'никој', u'никоја', u'никое', u'никои', u'ничиј', u'ничија', u'ничие', u'ничии',
       u'секој', u'секоја', u'секое', u'секои', u'сечиј', u'сечија', u'сечие', u'сечии',
       u'некој', u'некоја', u'некое', u'некои', u'нечиј', u'нечија', u'нечие', u'нечии'],
  'ZL':[u'јас', u'ти', u'тој', u'таа', u'тоа', u'ние', u'вие', u'тие',
        u'овој', u'оваа', u'ова', u'овие', u'оној', u'онаа', u'она', u'оние'],
  'SV':[u'и', u'или', u'а', u'дека', u'но', u'туку', u'така'],
  'PD':[u'низ', u'од', u'до', u'на', u'врз', u'под', u'зад', u'во', u'преку', u'покрај',
        u'кон', u'со', u'пред'],
  'PL':[u'долго', u'кратко'],
  'PT':[u'да'],
  'G': [u'е']}

_inv_exact = dict((w, tag_)
                  for tag_, words in _exact.iteritems()
                  for w in words)
_base_tags = {
  'GP':   'PL',
  'NSV':  'G',
  'NSVL': 'G',
  'GL':   'G',
  'GP3':  'G',
  'PRMC': 'PR',
  'PRP':  'PR',
  'PRPC':  'PR',
  'GI':   'I',
  'IM':   'I',
  'IMP':   'I',
  'IP':   'I',
  'IPC':   'I',
  'IMC':   'I',
  'IF':   'I',
  'IFC':  'I',
  'IFP':  'I',
  'IFPC': 'I',
  'ZL':   'Z'}


def tag(token, base = True):
    """Returns guessed tag for a token, returns None if fails to tag.
    If `base` - it will return a base tag"""
    if token.isdigit():
        return 'NU'

    tag_ = _inv_exact.get(token.lower(), None)
    if tag_ is not None:
        if base:
            return _base_tags.get(tag_, tag_)
        return tag_

    for ext, tag_ in _ext.iteritems():
        if token.endswith(ext):
            if base:
                return _base_tags.get(tag_, tag_)
            return tag_

    return None

def iter_tagged(tokens):
    """Iterates pairs token, tag for a sequence of tokens"""
    for t in tokens:
        yield t, tag(t)

"""Function to return the base tag for a given tag"""
base_tag = lambda tag: _base_tags.get(tag, tag)

def build_tagger(tokens):
    """Build tagger from basic analysis of a token stream"""
    trigrams = iter_ngrams(tokens, 3)

    tagger = {'L':defaultdict(list), 'M':defaultdict(list), 'R':defaultdict(list)}

    builder_skip_tags = set(('NU', 'PU'))

    for l, m, r in trigrams:
        lt, mt, rt = map(tag, (l, m, r))
        if reduce(or_, [tag_ is None for tag_ in (lt, mt, rt)]): continue

        if lt not in builder_skip_tags:
            tagger['L'][(mt, rt)].append(lt)
        if mt not in builder_skip_tags:
            tagger['M'][(lt, rt)].append(mt)
        if rt not in builder_skip_tags:
            tagger['R'][(lt, mt)].append(rt)

    return tagger
