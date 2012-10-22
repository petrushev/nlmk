
from collections import deque

def multi_ngram(tokens, top_n):
    """Create ngram counted dictionaries up to `top_n` ngram"""
    history = [deque() for _ in range(top_n-1)]
    
    res = [{} for _ in range(top_n)]
    for tk in tokens:
        if not tk.isalpha():
            history = [deque() for _ in range(top_n-1)]
            continue
        tk = tk.lower()

        res[0][(tk,)] = res[0].get((tk,), 0) + 1

        for i in range(top_n-1):
            history[i].append(tk)
            if len(history[i])==i+2:
                tpl = tuple(history[i])
                res[i+1][tpl] = res[i+1].get(tpl, 0) + 1
                history[i].popleft()
        
    return res

def cutt_ngrams(ngrams, cuttoff_info):
    """Cut the `ngrams` dictionaries for rare matches"""
    for i in range(len(ngrams)):
        cuttoff = cuttoff_info[i]
        ngrams[i] = dict( (key, val)
                         for key, val in ngrams[i].iteritems()
                         if val >= cuttoff)
    return ngrams

