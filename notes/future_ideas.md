This lists stuff I don't have time to do now, but could look at in
the future.

## Names allowed in kanji

 data/chars_allowed_in_names

 - would be interesting to generate a gender graph of these
 - small kana are allowed
 - other old kana (wo, we, wi) are allowed
 - small wa is allowed
 - ゝゞ are allowed

## Fixing suo

{"kaki": "周防 正行", "yomi": [-"すお-]{+"すおう+} まさゆき", "authenticity": "real", "lifetime": {"birth_year": 1956, "death_year": null}, "source": "wikipedia_en:Masayuki Suo", }

すお is a valid reading for the surname, but rare enough that we assumed
the longer one. The Wikipedia JA fixes this so one valid solution would
be to ignore entries where we have a JA article. We could also detect this
at dedupe perhaps.

Could check how many new names we're actually getting from EN, it's possible
most of the EN articles (after dedupe) are just erroneous forms of JA articles.

## More robust handling of 'yuhya'-type names

Currently we use a manual dictionary to correct these.

## 反り目、反リ目 (etc.) ought to be treated identically

## Pitch accents

 - see pitch text.

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

## seijiyama improvements

  - go back and scrape missing cards (currently we ignore things we have
    \> 5 hits for)

## yuuki / yuki and other stuff

For some names (ゆうき・ゆき) perhaps we shouldn't even generate records, as they
would bias the stats? Picking randomly doesn't work either if it's gender-based.

For example ochi/大内 has two readings おおち、おうち, clearly either of them is better
than returning おち!
 - I think we currently do this (only messy romajise one part, not both) but
   need to check

 - How much effort do we want to expend? How much of the database is xx-romaji?

## Importer module

A module to handle logging, execution time, validation, errors/okays
etc. would be useful here.

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

* https://oneosaka.jp/member/
* https://www.wasedarugby.com/member_list/
* http://kazina.com/dummy/

* https://www.tus.ac.jp/today/archive/20210705_2485.html - 大翔 readings split (and 結愛)
* https://www.j-clip.co.jp/narrator/
* https://gendai.ismedia.jp/articles/-/63867?page=3

* (main dict) http://www.practical-japanese.com/

## Other name data (?)

* https://pon-navi.net/nazuke/name/ranking
* https://b-name.jp/
* https://name-power.net/

## Tagging name splits

It's useful to tag anywhere we performed a manual data split, and
avoid using that data (at least in preference) when splitting again.
Frequency data is not considered when splitting.

 ... for example such entries can be ignored when building RomajiDB,
     which could be used as a hint for splitting kanji (rather than JMnedict)

 - low priority - not many false positives there

## Gender data

### JA wikipedia name pages

There are pages for genders that might provide extra dictionary data:

https://ja.wikipedia.org/wiki/Category:日本語の女性名 (男性名・姓)

  日本の女性名。現代では主に「あきこ」、まれに「めいこ」と読むが、平安時代には「あきらけいこ」と読まれた。
  日本人の人名。主に女性名に使われる。
  敦子（あつこ）は、日本の女性名。

### Wikidata gender override

wikidata is sometimes wrong about gender. We could override it if we have
enough data, e.g. wikipedia en/ja disagree with it. Currently we just take
the majority.

## Counters

 - categories (time / food / etc.)
 - rarity within category
 - implement tidy-up code and sanity checker

 https://www.benricho.org/kazu/index.html
 https://www.sanabo.com/kazoekata/

## Refactor

 - Should probably ensure only one set of subreadings exists.
 - Map names back to sources?

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

Could be done by the app itself.

### Weird missing 'いち', and 'りよう' entries

Fun stuff here (17 hits):

    "kaki": "京子",
    "yomi": "きようこ",
               ^
    "kaki": "純一",
    "yomi": "じゆんいち",
               ^
Oh boy...

    "kaki": "淳一",
    "yomi": "じゆんいち",
               ^
    "kaki": "亮",
    "yomi": "りよう",
               ^
From wikipedia and also researchmap:
jsonl/researchmap.jsonl:{"kaki": "吉田 亮", "yomi": "よしだ りよう", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "researchmap", "tags": ["person"]}
For 'ryou', 274 of these vs. 8830 total. So not too bad. But annoying.

### 井

There are a few results of 'ii' for these names, possibly because websites
reject names of 1 char in length. Maybe we should override these as ii
is not a regular reading. 伊 doesn't have this problem (although 'ihn' is
occasionally seen).

### All or nothing

Could tag individual parts of the name with xx-romaji if we had dictionary
data for some but not all?
 e.g. xx-romaji-sei, xx-romaji-mei

## Other dictionaries

These are less important as wikipedia_ja accounts for 90% of all
name records among the wiki/dictionary sources.

### Use the Researchmap code in all importers

Wikidata etc. should use the same researchmap code that already
handles clever stuff.

 namedata, err = intuit_name_data(kana, kanji, romaji)

{"kaki": "奥田 教介", "yomi": "おくだ きょすけ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "source": "wikidata:http://www.wikidata.org/entity/Q106392717", "tags": ["xx-romaji", "masc", "person"]}

^ this for example.

### Related: make romaji_to_hiragana_fullname swap names for you

This would simplify logic in both researchmap and wikidata_nokana.

### koujien

Fails to split in some places, could be fixed by using RomajiDB

## wikidata: de-dupe variant records

Somehow when removing nakaguro I stripped 300 records from wikidata.jsonl?
I think due to the seen() stuff? None of my code would have changed it, yet
the .old version has 2 copies of Q55526706

Change unique key to (Q, birth_date % 2, kanji) ?
 if kanji is not split, don't store it? or warn
 Check for unsplit people

        # TODO we also get dupe records with different kanji/kana combinations,
        #      only some make sense. Whoops. e.g. https://www.wikidata.org/wiki/Q6753582
        #      has two 'name in kana', only one makes sense.
        # TODO we could improve this by doing all of them then outputting the 'best'
        #      e.g. the one we were able to split.
        # Dump has 143,141 unique names and 147,676 records - so not a major problem,
        # but could return incorrect readings.

Some records make no sense and could be rejected, e.g.
jsonl/wikidata.jsonl:{"kaki": "河野悠里", "yomi": "だいぜんじ ふみこ", "authenticity": "real", "lifetime": {"birth_year": 1983, "death_year": null}, "subreadings": [], "source": "wikidata:http://www.wikidata.org/entity/Q11554202", "tags": ["fem"]}

[**] Also need a re-run for katakana handling update.
