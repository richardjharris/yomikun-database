## Ideas

 - Person merge could maybe resolve 2 M + 1 F as just M (if wikidata is the wrong one)
   房之介 appears in wikidata as female (incorrectly) and male in
   wikipedia\_en, \_ja (correctly).

 - The last 'two' kana of a name are useful for gender determination, could include
   that.

```
{"kaki": "夏目 房之介", "yomi": "なつめ ふさのすけ", "authenticity": "real", "lifetime": {"birth_year": 1950, "death_year": null}, "subreadings": [], "source": "wikipedia_ja:夏目房之介", "tags": ["person", "masc"]}
{"kaki": "夏目 房之介", "yomi": "''なつめ ふさのすけ''", "authenticity": "real", "lifetime": {"birth_year": 1950, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Fusanosuke Natsume", "tags": ["masc", "person"]}
```

稲荷家房之介 has male/female entries due to wikidata. Also years are different, so we don't
merge in any case. That's probably fine.

### JA wikipedia pages

We could use the info in JA wikipedia pages to populate a gender dictionary. This could be
semi-automated.

As a start: https://ja.wikipedia.org/wiki/Category:日本語の女性名 and equivalent (and 日本語の姓)
Each page has some information: 
  日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
  日本人の人名。主に女性名に使われる。
  敦子（あつこ）は、日本の女性名。
