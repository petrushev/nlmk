from sys import argv
from nlmk import ngramgen as ngramgenmod

import codecs
from nlmk import text
from nlmk import tokenizer

def ngramgen(source, *cuttoff_info):
    """Generate n-grams with provided cuttoff"""

    try:
        fh = codecs.open(source, 'r', 'utf-8')
    except Exception:
        raise
        return

    try:
        cuttoff_info = map(int, cuttoff_info)
    except ValueError:
        print 'Invalid cuttoff info provided, list of integers needed'
        return

    if len(cuttoff_info) == 0:
        print 'Cuttoff info provided is zero length'
        return


    content = fh.read()

    fh.seek(0)
    sent_idx = tokenizer.sentences_index(content)
    del content

    fh.seek(0)
    isents = text.iter_sentences(fh, sent_idx)

    itokens = (t for t, s, tid in text.iter_tokens(isents))
    res = ngramgenmod.multi_ngram(itokens, len(cuttoff_info))
    fh.close()

    res = ngramgenmod.cutt_ngrams(res, cuttoff_info)

    for dict_ in res:
        for tpl, v in dict_.iteritems():
            print (' '.join(tpl) + ' ' + unicode(v)).encode('utf-8')


_runners = {'ngramgen': ngramgen}

def main():
    try:
        case = argv[1]
    except IndexError:
        print('No runner provided.')
        return

    if case == 'main': return

    try:
        case = _runners[case]
    except KeyError:
        print 'Runner %s not found.' % case
        print 'Available runners:'
        for runner, runner_fc in _runners.iteritems():
            print '    %s: %s' % (runner, runner_fc.__doc__)
        return

    args = argv[2:]
    case(*args)


if __name__ == '__main__':
    main()
