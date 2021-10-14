This lists stuff I don't have time to do now, but could look at in
the future.

## More robust handling of 'yuhya'-type names

Currently we use a manual dictionary to correct these.

## Name lists online

Could develop a crawler + extractor for these.

* https://www.chuobyoin.or.jp/doctor/
* https://www.bungelingbay.com/gym/staff-reigo-sirai/
* https://www.niraidai.net/professor/professor.html
* https://www.k-1.co.jp/fighter/828/
* https://en.wikipedia.org/wiki/Toma_Kuroda
* https://toyokeizai.net/list/ranking
* https://48pedia.org/%E5%85%A8%E3%83%A1%E3%83%B3%E3%83%90%E3%83%BC%E3%81%AE%E4%B8%80%E8%A6%A7#AKB48
* http://keirin.jp/pc/racerprofile?snum=015518

* http://sakurashigikai.gijiroku.com/g07_giinlistP.asp - lots of these, doing some
* https://oneosaka.jp/member/
* https://seijiyama.jp/area/table/3811/B0qbJG/M?S=rcla2ldnbk - 1.3M records (or 1368 fetches)

 Just do https://seijiyama.jp/area/table/3811/B0qbJG/M?detect=%94%BB%92%E8&_limit_13878=100&S=rcla2ldnbk&_page_13878=1
   with each page
   Then parse out
   Sub-pages have age, gender.
   Some are dupes (しまじり　あいこ has 3 entries). Some have no furigana.

 * https://www.wasedarugby.com/member_list/

## Other name data (?)

* https://pon-navi.net/nazuke/name/ranking

## Tagging name splits

It's useful to tag anywhere we performed a manual data split, and
avoid using that data (at least in preference) when splitting again.
Frequency data is not considered when splitting.

 ... for example such entries can be ignored when building RomajiDB,
     which could be used as a hint for splitting kanji (rather than JMnedict)
     However RomajiDB would need to support >1 reading first.

## Gender data

### JA wikipedia name pages

There are pages for genders that might provide extra dictionary data:

https://ja.wikipedia.org/wiki/Category:日本語の女性名 (男性名・姓)

  日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
  日本人の人名。主に女性名に使われる。
  敦子（あつこ）は、日本の女性名。

### Wikidata gender override

wikidata is sometimes wrong about gender. We could override it if we have
enough data, e.g. wikipedia en/ja disagree with it.

Example: 房之介 m m f

### Last two kana of name

Last two kana of name (not just first) is a useful vector. This is based
on reading baby name books.

## Counters

 - categories (time / food / etc.)
 - rarity within category
 - implement tidy-up code and sanity checker

## Refactor

 - Remove subreadings system, replace with `list[NameData]`
 - Force 'person' tag
 - Remove gender tags from jmnedict data to avoid special casing (?)
 - Map names back to sources

## Flutter app

## Bugs

### JA Wikipedia

# 士郎 正宗

Pen name according to wiki-en, but we reported 'real'.
To fix this we'd need to use wikidata to collect interlanguage links, to notice
that all the records are for the same person.

### EN Wikipedia

 - https://en.wikipedia.org/wiki/Shingo\_Tano

Born name in infobox.
