#!/usr/bin/env python
# -*- coding: utf-8 -*-
from prosecco import *

text = """Chrząszcz brzmi w trzcinie w Szczebrzeszynie.
Ząb zupa zębowa, dąb zupa dębowa.
Gdzie Rzym, gdzie Krym. W Pacanowie kozy kują.
Tak, jeśli mam szczęśliwy być, to w Gdańsku muszę żyć! 
"""

cities = ["szczebrzeszyn", "pacanow", "gdansk", "rzym", "krym"]
conditions = []
# accept all
for city in cities:
    conditions.append(Condition(lemma_type="city",
                                compare=city,
                                normalizer=CharsetNormalizer(Charset.PL_EN),
                                stemmer=WordStemmer(language="pl"),
                                lower=True))
# accept all
conditions.append(Condition(compare=r".*"))

tokenizer = LanguageTokenizer(Charset.PL)
tokens = tokenizer.tokenize(text)
visitor = Visitor(conditions=conditions)
lexer = Lexer(tokens=tokens, visitor=visitor)
lemmas = lexer.lex()
found_cities = filter(lambda l: l.type == 'city', lemmas)
print(" ".join(map(str, found_cities)))
