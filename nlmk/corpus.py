
def tf_distribution(tokens):
    """Given a token stream (a document) returns term frequency distribution
       for all tokens, normalized with the maximum frequency"""
    tf_dist = {}
    max_ = 0
    for token in tokens:
        tf_dist[token] = tmp = tf_dist.get(token, 0) + 1
        if tmp > max_: max_ = tmp

    norm = 1.0/max_
    return dict((token, val*norm)
                for token, val in tf_dist.iteritems())
