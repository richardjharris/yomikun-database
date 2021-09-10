## Ideas

 - For each first name in wikipedia_ja (for example) try to compute
   the gender.

    Resources: data/name_lists.json (reading)
               average gender for kana reading
               average gender for kanji reading (*)
               guess based on kanji inside
               guess based on name length (4+ is usually male)
               manual overrides

    For cross checking: baby names site, namegen, JA wikipedia pages
    
    We can then compute a name dictionary which can be looked up
    independently of everything else.

    Where the results differ from reality, we tweak the algorithm.

### Notes

 * wikidata/wikipedia data is heavily male biased, about 75% male
   on average (probably due to politicans + sports + historical
   figures).

   For example, makoto is 85% male in wiki data. akira is ~99% male.

   However at the kanji level, individual kanji show much stronger
   rates of male/female exclusivity, e.g. 誠 vs. 真琴
   Also, the wiki page says makoto is gender-neutral.
   [Interestingly 真恋人 is missing from namegen, but we have it!]

 * try extracting gender info from japanese wikipedia again. e.g. extract
   女 (exclusing 帰国子女). This would help to identify more female names,
   as women are marked more often than men.

### JA wikipedia pages

　As a start: https://ja.wikipedia.org/wiki/Category:日本語の女性名 and equivalent (and 日本語の姓)
  Each page has some information: 
    日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
    日本人の人名。主に女性名に使われる。
    敦子（あつこ）は、日本の女性名。

The EN wikipedia has similar pages, e.g. https://en.wikipedia.org/wiki/Hirotomo which mark the
gender clearly and show common readings.