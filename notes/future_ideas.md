This lists stuff I don't have time to do now, but could look at in
the future.

## More robust handling of 'yuhya'-type names

Currently we use a manual dictionary to correct these.

## Kanji picker

A better kanji picker. Top/bottom slots, pick radical, etc.

## More robust romaji to hiragana conversion

Instead of simplifying romaji to a romaji key (which loses data)
we could generate all possible romaji forms of a word in RomajiDB
then look the form up directly.

For example 後藤(ごとう) would generate goto gotou gotoh goto (macron)
俊平（しゅんぺい） could generate shunpei, shumpei, shumpeh (?)

Could get unweildly quickly. But it allows us to use all the data
in the original romaji, e.g. if macrons are used they'll be respected.

 - this would be useful for 'りよう' and friends, where the small
   kana is large instead. But equally we could romaji_key ryo -> riyo
   to handle this.

## Okinawan names

https://www.shurei.com/

## Nagoya who's-who database

https://jahis.law.nagoya-u.ac.jp/who/search  (multiple editions)

## Wikipedia JA gender

If we compute all subcategories belonging to the root 'Japanese women'
category we can match against that instead of handcrafted patterns.

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
* https://www.wasedarugby.com/member_list/
* http://kazina.com/dummy/
 

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

## JA Wikipedia - names inside articles

Crawl for names **inside** articles (e.g. in kanji(kana) form). Most of these
are character names, but probably still useful for reading data.

## Alternate kanji forms

Names like Akira Kurosawa and many old names have multiple forms. Currently we
handle this by making duplicate records, but it would be better to tolerate common
pairings like 高・髙 (for 髙木). OTOH alt forms seem to be collocated with particular
kanji most of the time (木 in this case), so not a priority.

## MeCab data

 - Not sure how to use. Probably overlaps with jmnedict