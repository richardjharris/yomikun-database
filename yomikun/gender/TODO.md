### Notes

  https://ja.wikipedia.org/wiki/%E9%95%B7%E6%BE%A4%E5%92%8C%E6%98%8E was marked
  as female, so maybe too many FPs. 長澤和明
  otoh we only got 1 fem result so we can determine FP easily here.

  Script works, we just need to make a judgement.

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
     - done: 29,356 female; 8,642 male (out of 218,418 entries)

    - wikipedia_ja:小出真朱 should not be marked as real.
    -  ditto https://ja.wikipedia.org/wiki/%E6%A2%93%E7%9C%9F%E5%BC%93

### JA wikipedia pages

　As a start: https://ja.wikipedia.org/wiki/Category:日本語の女性名 and equivalent (and 日本語の姓)
  Each page has some information: 
    日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
    日本人の人名。主に女性名に使われる。
    敦子（あつこ）は、日本の女性名。

The EN wikipedia has similar pages, e.g. https://en.wikipedia.org/wiki/Hirotomo which mark the
gender clearly and show common readings.