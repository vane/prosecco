prosecco
====

[![GitHub](https://img.shields.io/github/license/vane/prosecco)](https://github.com/vane/prosecco/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/prosecco)](https://pypi.org/project/prosecco/)
[![GitHub last commit](https://img.shields.io/github/last-commit/vane/prosecco)](https://github.com/vane/prosecco)

  
## Description

Slim, flexible and extendable NLP engine that can produce list of features 
from text based on provided condtions.  

## Features
- word categorisation
- feature extraction 

## Install
```bash
pip install prosecco
```
## Usage

### Basic
```python
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
lemmas  = set(p.get_lemmas(type='hero'))
print(" ".join(map(str, lemmas)))
```

### Output
```Batman[hero][start:1090] Black Panther[hero][start:17691] Superman[hero][start:2071] Captain Marvel[hero][start:3703]```

### Advanced

```python
from prosecco import *

text = """Chrząszcz brzmi w trzcinie w Szczebrzeszynie.
Ząb zupa zębowa, dąb zupa dębowa.
Gdzie Rzym, gdzie Krym. W Pacanowie kozy kują.
Tak, jeśli mam szczęśliwy być, to w Gdańsku muszę żyć! 
"""

# 1. Create conditions based on city names
cities = ["szczebrzeszyn", "pacanow", "gdansk", "rzym", "krym"]
conditions = []
for city in cities:
    conditions.append(Condition(lemma_type="city",
                                compare=city,
                                normalizer=CharsetNormalizer(Charset.PL_EN),
                                stemmer=WordStemmer(language="pl"),
                                lower=True))
# 2. Create tokenizer for polish charset
tokenizer = LanguageTokenizer(Charset.PL)
# 3. Get list of tokens
tokens = tokenizer.tokenize(text)
# 4. Create visitor with conditions provided in step 1
visitor = Visitor(conditions=conditions)
# 5. Parse tokens based on visitor conditions
lexer = Lexer(tokens=tokens, visitor=visitor)
# 6. Get list of lemmas
lemmas = lexer.lex()
# 7. filter found cities
found_cities = filter(lambda l: l.type == "city", lemmas)
# 8. print output
print(" ".join(map(str, found_cities)))
```   

### Output
```Szczebrzeszynie[city][start:29] Rzym[city][start:86] Krym[city][start:98] Pacanowie[city][start:106] Gdańsku[city][start:163]```
