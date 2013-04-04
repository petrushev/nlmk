Natural Language processing library for Macedonian (MK)
=======================================================

**nlmk** is a small library for nlp specialized for Macedonian language, focusing on localization of the tokenizer and the stopwords and it also provides document analysis. People familiar with ``nltk`` (``python``) can be introduced painlessly. It also has focus on working with large files (texts).

Requirements
------------

``nlmk`` requires the following third party libraries:
 - ``pyparsing-1.5.7``

``nlmk`` can also run with ``pypy``. Please be careful to install the correct ``pyparsing`` version.

Fetch sentences
---------------

Display part of text, specified as a sentence-slice.

Examples:
::

    python run.py sentences corpus/racin.txt 7
    python run.py sentences corpus/racin.txt :2
    python run.py sentences corpus/racin.txt 3:10
    python run.py sentences corpus/racin.txt 80:

Concordance
-----------

Display a word occuring in a fixed-length window (default: 9).

Examples:
::

    python run.py concordance corpus/racin.txt филозофија
    python run.py concordance corpus/racin.txt филозофија 2

N-gram extraction from texts
----------------------------

Use the ``nlmk.ngramgen`` module, or call it through the ``run.py`` caller.

Example:
::

    python run.py ngramgen corpus/racin.txt 10 2 1

This will generate unigrams, bigrams and trigrams:

    - the unigrams (words) show up at least 10 times
    - the bigrams occur at least 2 times
    - the trigrams occur at least 1 time (all trigrams)

POS-tagers
----------

Use the ``nlmk.tagger`` module, or call it through the ``run.py`` caller.

Example:

First you need to build a tagger using one or more documents. This will build a tagger called ``sociology``:
::

    python run.py build-tagger sociology corpus/obezvrednuvanje.na.trudot.txt corpus/rabotni.sporovi.txt

This tagger can be used to tag some other documents:
::

    python run.py tag corpus/racin.txt sociology

Term frequency
--------------

Use ``nlmk.corpus`` module, or call it through the ``run.py`` caller.

Example:

This will give the term frequency distribution:
::

    python run.py tf corpus/racin.txt
