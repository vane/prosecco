#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple, extendable nlp engine that can extract data based on provided conditions.
"""

__version__ = "0.0.4"
import os
import os.path
import sys
import re
from lib.model import *
from lib.normalizer import *


# -------------
# Stemmer
# -------------
class SuffixStemmer:
    """
    Base class for stemming words
    Return tuple of stemmed outputs
    """
    def __init__(self, language, path=None):
        self.language = language
        self.stemwords = ()
        if path is None:
            path = os.path.dirname(__file__)+"/data/{}/suffix.txt".format(language)
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
        for i, character in enumerate(text):
            # pick
            if character.lower() in self.charset:
                partial += character
            else:
                if len(partial) > 0:
                    tokens.append(Token(token=partial, end=i))
                    partial = ""
                tokens.append(Token(token=character, end=i))
        if len(partial) > 0:
            tokens.append(Token(token=partial, end=i))
        return tokens


# -------------
# Lexer / Visitor
# -------------
class Visitor:
    """
    Utility class for Lexer that use Condition class to check wheather
    we add Lemma to Lexer output or process list of tokens further
    """
    def __init__(self, conditions, empty=True, auto_space=False, num_words=10):
        self.conditions = conditions
        # empty lexer token list
        self.empty = empty
        self.auto_space = auto_space
        self.lemma = None
        self.num_words = num_words

    def __contains__(self, item):
        # get items of size num_words
        item_copy = item[-self.num_words:]
        while len(item_copy) > 0:
            # make sentence from list of item
            if self.auto_space:
                data = Lemma.filter_space(item_copy)
                sentence = Lemma.build_sentence(data, separator=" ")
            else:
                sentence = Lemma.build_sentence(item_copy)
            # check sentence against conditions
            for condition in self.conditions:
                if sentence in condition:
                    self.lemma = Lemma(type=condition.lemma_type,
                                       data=item_copy[:],
                                       condition=condition.found,
                                       sentence=sentence)
                    return True
            item_copy.pop(0)
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
        return [l for l  in self.lemmas if re.match(type, l.type)]
