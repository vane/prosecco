prosecco
====

[![GitHub](https://img.shields.io/github/license/vane/prosecco)](https://github.com/vane/prosecco/blob/master/LICENSE)
[![pypi](https://img.shields.io/pypi/v/prosecco)](https://pypi.org/project/prosecco/)
[![GitHub last commit](https://img.shields.io/github/last-commit/vane/prosecco)](https://github.com/vane/prosecco)

  
## Description

Simple, extendable nlp engine that can extract data based on provided conditions.  
 

## Install
```bash
pip install prosecco
```
## Usage

### Basic
```python
from prosecco import Prosecco, Condition, EnglishWordNormalizer

# Read wikipedia https://en.wikipedia.org/wiki/Superhero
with open("superhero.txt") as f:
    text = f.read()

# 1. Create conditions with hero names
conditions = [
    Condition(lemma_type="hero|dc", compare=["batman", "superman", "wonder woman"], lower=True),
    Condition(lemma_type="hero|marvel", normalizer=EnglishWordNormalizer(),
              compare=["spiderman", "iron man", "black panther"], lower=True)
]
# 2. Create prosecco
p = Prosecco(conditions=conditions)
# 3. Let's drink and print output
p.drink(text, progress=True)
lemmas  = set(p.get_lemmas(type="hero"))
print(" ".join(map(str, lemmas)))
```

### Output
```Batman[hero|dc][start:1090] Wonder Woman[hero|dc][start:2101] Captain Marvel[hero|marvel][start:3703] Superman[hero|dc][start:2071] Spider-Man[hero|marvel][start:2081] Black Panther[hero|marvel][start:17691]```

### Advanced

```python
from prosecco import *

text = """Chrząszcz brzmi w trzcinie w Szczebrzeszynie.
Ząb zupa zębowa, dąb zupa dębowa.
Gdzie Rzym, gdzie Krym. W Pacanowie kozy kują.
Tak, jeśli mam szczęśliwy być, to w Gdańsku muszę żyć! 
"""

# 1. Create condition with city names
cities = ["szczebrzeszyn", "pacanow", "gdansk", "rzym", "krym"]
animals = ["koz", "chrzaszcz"]
# 2. Normalizer to remove polish specific charset
n = CharsetNormalizer(Charset.PL_EN)
# 3. Stemmer to remove suffix
s = SuffixStemmer(language="pl")
# 4. Conditions for city and animal
city_condition = Condition(lemma_type="city", compare=cities, normalizer=n, stemmer=s, lower=True)
animal_condition = Condition(lemma_type="animal", compare=animals, normalizer=n, stemmer=s, lower=True)
conditions = [city_condition, animal_condition]
# 5. Create tokenizer for polish charset
tokenizer = LanguageTokenizer(Charset.PL)
# 6. Get list of tokens
tokens = tokenizer.tokenize(text)
# 7. Create visitor with conditions provided in step 1
visitor = Visitor(conditions=conditions)
# 8. Parse tokens based on visitor conditions
lexer = Lexer(tokens=tokens, visitor=visitor)
# 9. Get list of lemmas
lemmas = lexer.lex()
# 10. filter found cities and print output
found = filter(lambda l: l.type == "city", lemmas)
print(" ".join(map(str, found)))
# 11. filter found anumals and print output
found = filter(lambda l: l.type == "animal", lemmas)
print(" ".join(map(str, found)))
```   

### Output
```bash
Szczebrzeszynie[city][start:29] Rzym[city][start:86] Krym[city][start:98] Pacanowie[city][start:106] 
Gdańsku[city][start:163]
Chrząszcz[animal][start:0] kozy[animal][start:116]
```
