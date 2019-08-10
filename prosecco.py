#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Short, flexible and extendable NLP engine that can produce list of features from text based on provided condtions.
I use it for :
- word categorisation
- feature extraction
"""
__version__ = '0.0.1'
import os
import re


# -------------
# Charset
# -------------
class Charset:
    """
    Provides information about character set for LanguageTokenizer
    All other characters will be treet as single tokens
    """
    EN = "qwertyuiopasdfghjklzxcvbnm1234567890"
    PL = EN+'ęóąśłżźćń'
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
    def __init__(self, conditions, empty=True, auto_space=True):
        self.conditions = conditions
        # empty lexer token list
        self.empty = empty
        self.auto_space = auto_space
        self.lemma = None

    def filter_space(self, data):
        return list(filter(lambda x: x != " ", data))

    def __contains__(self, item):
        if self.auto_space:
            data = self.filter_space(item)
            sentence = " ".join(data)
        else:
            sentence = " ".join(item)
        for condition in self.conditions:
            if condition == sentence:
                self.lemma = Lemma(type=condition.lemma_type, data=sentence)
                return True
        return False


class Lexer:
    """
    Converts list of tokens based on conditions in LexVisitor
    """
    def __init__(self, tokens, visitor):
        self.tokens = tokens
        self.visitor = visitor

    def lex(self):
        lemma_list = []
        token_list = []
        for token in self.tokens:
            token_list.append(token)
            if token_list in self.visitor:
                lemma_list.append(self.visitor.lemma)
                if self.visitor.empty:
                    token_list = []
        return lemma_list


# -------------
# Lemma
# -------------

class LemmaType:
    SKIP = "skip"
    KEY = "key"

class Lemma:
    """Base lemma class output for lexer"""
    def __init__(self, type, data):
        self.type = type
        self.data = data

    def __repr__(self):
        return "{}[{}]".format(self.data, self.type)


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
