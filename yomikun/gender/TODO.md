## Ideas

 - xref wikipedia name lists (male/female/unisex) with our data,
   is it representatative? probably male
   bias - what gender split is the wikipedia extracted data?

    % female / f+m
    wikidata: 34687/103443  -> 25%
    ..nokana:                  30%
    wiki-en                    26%
    jmnedict is >90% female, which seems weird. Perhaps the assumption
    is male?

    wikipedia_en makoto: ~85% male
    wikidata: >92% male

    akira: 957/1000 wikidata are male, 114/120 wikipedia EN are male.

    However the split is good for kanji: 誠 vs. 真琴 etc provides a reasonable
    guess. Interestingly 真恋人 is missing from namegen, but we have it.

 - try extracting gender info from japanese wikipedia again. e.g. extract
   女 (exclusing 帰国子女).

 - try wikidata, which has gendered info?
   -> done.

Goal: given a name (written/reading) return the rough % chance of it being male.
Data sources:
 - EN wikipedia has pages for male, female and unisex names, based on reading only.
   It seems pretty good. There are some hints in each article re: the name being
   'commonly' or 'predominantly' male.

 - JA wikipedia has a smaller list, but might contain some other names.

 - EN wikipedia articles for Japanese reveal the gender based on he/his or she/her
   in the article text. So it may be worth reading this dump too.
     - The EN wikipedia seems more up to date, and probably more comprehensive
       in terms of article count. I found several names not in the JA wikipedia.

## Name genders

　As a start: https://ja.wikipedia.org/wiki/Category:日本語の女性名 and equivalent (and 日本語の姓)
  Each page has some information: 
    日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
    日本人の人名。主に女性名に使われる。
    敦子（あつこ）は、日本の女性名。

 The EN wikipedia has similar pages, e.g. https://en.wikipedia.org/wiki/Hirotomo which mark the gender clearly
 and show common readings. Most of the names themselves are in the JA wikipedia though.
