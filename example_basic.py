#!/usr/bin/env python
# -*- coding: utf-8 -*-
from prosecco import Prosecco, Condition

# Read wikipedia https://en.wikipedia.org/wiki/Superhero
with open('sample/superhero.txt') as f:
    text = f.read()

# 1. Create conditions based on super hero names
superheroes = ["batman", "spiderman", "superman", "captain marvel", "black panther"]
conditions = [Condition(lemma_type="hero", compare=hero, lower=True) for hero in superheroes]
# 2. Create prosecco
p = Prosecco(conditions=conditions)
# 3. Let's drink and print output
p.drink(text, progress=True)
lemmas = set(p.get_lemmas(type='hero'))
print(" ".join(map(str, lemmas)))

