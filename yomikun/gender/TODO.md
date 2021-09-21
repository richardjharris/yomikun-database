## Objectives

To be able to answer questions like:

 * given a kanji or kana given name, what is the likely gender?
 * what are the most unisex names?
 * what kanji versions of a particular kana name are most often
   associated with men or women?

For improving our data:

 * what names have zero or very few gender-tagged results?

## Ideas

 - Try to remove FPs via person merging
   房之介 appears in wikidata as female (incorrectly) and male in
   wikipedia_en, _ja (correctly).

### JA wikipedia pages

We could use the info in JA wikipedia pages to populate a gender dictionary. This could be
semi-automated.

As a start: https://ja.wikipedia.org/wiki/Category:日本語の女性名 and equivalent (and 日本語の姓)
Each page has some information: 
  日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
  日本人の人名。主に女性名に使われる。
  敦子（あつこ）は、日本の女性名。
