#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Slim, flexible and extendable NLP engine that can produce list of features from text based on provided condtions.
Use it for :
- word categorisation
- feature extraction
"""
__version__ = "0.0.3"
import os
import re
import sys


# -------------
# Charset
# -------------
class Charset:
    """
    Provides information about character set for LanguageTokenizer
    All other characters will be treet as single tokens
    """
    EN = "qwertyuiopasdfghjklzxcvbnm1234567890"
    PL = EN+"ęóąśłżźćń"
    PL_EN = { "ę": "e", "ó": "o", "ą": "a", "ś": "s", "ł": "l", "ż": "z", "ź": "z", "ć": "c", "ń": "n", }


class CharsetNormalizer:
    def __init__(self, charset):
        self.charset = charset

    def normalize(self, word):
        out = ""
        for c in word:
            if c in self.charset:
                if c.istitle():
                    c = self.charset[c].upper()
                else:
                    c = self.charset[c]
            out += c
        return out


# -------------
# Stemmer
# -------------
class WordStemmer:
    """
    Base class for stemming words
    Return tuple of stemmed outputs
    """
    def __init__(self, language, path=None):
        self.language = language
        self.stemwords = ()
        if path is None:
            path = "data/{}/suffix.txt".format(language)
        with open(path) as f:
            # read file strip \n sort by length and save as tuple
            w = [w.strip() for w in f.readlines()]
            w.sort(key=len)
            self.stemwords = tuple(w)

    def stem(self, word):
        stem_list = []
        for s in self.stemwords:
            if word.endswith(s):
                stem_list.append(word[:-len(s)])
        return tuple(stem_list)


# -------------
# Tokenzier
# -------------
class LanguageTokenizer:
    """Tokenize string of data to array of tokens"""
    def __init__(self, charset):
        self.charset = charset

    def tokenize(self, text):
        tokens = []
        partial = ""
        for c in text:
            # pick
            if c.lower() in self.charset:
                partial += c
            else:
                if len(partial) > 0:
                    tokens.append(partial)
                    partial = ""
                tokens.append(c)
        return tokens


# -------------
# Lexer / Visitor
# -------------
class Visitor:
    """
    Utility class for Lexer that use Condition class to check wheather
    we add Lemma to Lexer output or process list of tokens further
    """
    def __init__(self, conditions, empty=True, auto_space=True, num_words=10):
        self.conditions = conditions
        # empty lexer token list
        self.empty = empty
        self.auto_space = auto_space
        self.lemma = None
        self.item_index = 0
        self.num_words = num_words

    def filter_space(self, data):
        return list(filter(lambda x: x != " ", data))

    def __contains__(self, item):
        # get items of size num_words
        item_copy = item[-self.num_words:]
        while len(item_copy) > 0:
            # make sentence from list of item
            if self.auto_space:
                data = self.filter_space(item_copy)
                sentence = " ".join(data)
            else:
                sentence = " ".join(item_copy)
            item_copy.pop(0)
            # check sentence against conditions
            for condition in self.conditions:
                if condition == sentence:
                    self.lemma = Lemma(type=condition.lemma_type, data=sentence, condition=condition)
                    return True
        # now iterate every word
        for i in range(self.item_index, len(item)):
            word = item[i]
            for condition in self.conditions:
                if condition == word:
                    self.lemma = Lemma(type=condition.lemma_type, data=word, condition=condition)
                    return True
        # keep last iteration so it's faster
        if self.empty:
            self.item_index = len(item)
        return False


class Lexer:
    """
    Converts list of tokens based on conditions in LexVisitor
    """
    def __init__(self, tokens, visitor):
        self.tokens = tokens
        self.visitor = visitor

    def lex(self, progress=False):
        lemma_list = []
        token_list = []
        for i, token in enumerate(self.tokens):
            token_list.append(token)
            if token_list in self.visitor:
                lemma_list.append(self.visitor.lemma)
                if self.visitor.empty:
                    token_list = []
            if progress:
                sys.stdout.write("\r{}%".format(int(i/len(self.tokens)*100)))
        return lemma_list


# -------------
# Lemma
# -------------

class LemmaType:
    SKIP = "skip"
    KEY = "key"

class Lemma:
    """Base lemma class output for lexer"""
    def __init__(self, type, data, condition):
        self.type = type
        self.data = data
        self.condition = condition

    def __repr__(self):
        return "{}[{}]".format(self.data, self.type)

    def __eq__(self, other):
        return self.data == other

    def __ne__(self, other):
        return self.data != other

    def __hash__(self):
        # hack for set comparasion - probably need some smarter way to do it
        return 1

class Condition:
    """Base condition class contain compare statement"""
    def __init__(self, lemma_type=LemmaType.SKIP, compare=None, normalizer=None, stemmer=None, lower=False):
        self.lemma_type = lemma_type
        self.lower = lower
        self.compare = compare
        self.normalizer = normalizer
        self.stemmer = stemmer

    def __eq__(self, data):
        if self.lower:
            data = data.lower()
        if self.normalizer:
            data = self.normalizer.normalize(data)
        if self.stemmer:
            words = self.stemmer.stem(data)
            # we got list of words so compare if we found one
            for word in words:
                if word == self.compare:
                    return True
        # regex comparasion
        return re.match(self.compare, data)


# -------------
# Prosecco
# -------------
class Prosecco:
    """Let's drink"""
    def __init__(self, charset=Charset.EN, conditions=None, num_words=10):
        self.charset = charset
        self.conditions = conditions or [Condition(compare=r".*")]
        self.lemmas = []
        self.num_words = num_words

    def drink(self, text, progress=False):
        tokenizer = LanguageTokenizer(self.charset)
        tokens = tokenizer.tokenize(text)
        visitor = Visitor(conditions=self.conditions, num_words=self.num_words)
        lexer = Lexer(tokens=tokens, visitor=visitor)
        self.lemmas = lexer.lex(progress=progress)
        return self.lemmas[:]

    def get_lemmas(self, type):
        return filter(lambda l: l.type == type, self.lemmas)
