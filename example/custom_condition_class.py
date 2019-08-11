#!/usr/bin/env python
# -*- coding: utf-8 -*-
from prosecco import Prosecco, Lemma
from difflib import SequenceMatcher


class SequenceMatcherCondition:
    def __init__(self, compare, tolerance=0.90, lemma_type="test"):
        self.lemma_type = lemma_type
        self.compare = compare
        self.tolerance = tolerance
        self.found = None

    def __contains__(self, item):
        sentence, next_token = item
        sm = SequenceMatcher(None, self.compare, sentence).ratio()
        if sm >= self.tolerance:
            self.found = sentence
            return True
        return False

text = "This is test setence."

p = Prosecco(conditions=[SequenceMatcherCondition(compare="sentence")])
lemmas = p.drink(text=text)
print(lemmas)
