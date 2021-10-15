## Romaji to kana conversion

Current task: finish researchmap import [DONE]
 - maybe look at the 'messy conversions' and add custom.csv entries.
 - there are 3,293 xx-romaji entries. [3,255 errors]
 - still going to be a WIP

 - Convert trailing 'ow' to 'oh'
 - Handle 'm' e.g. 'mp', 'mb'

I've cleaned up double-barreled names, middle initials, most dots, 'III'
Not properly checked for >2 names (especially >2 kana in 1st column)

Some fun readings to check:

 - Rare 雅篤 [masa-atsu]
 - 大洞 将嗣	Oh-hora Masatsugu
 - 寺澤 知潮	Tomo-o Terasawa
 - 廣瀬 貴章	廣瀬 貴章	Taka-aki Hirose
 - 木村 善一郎	Kimura Zen-ichiro
 - 松裏 恵子	Keiko Matsuura
 - 大竹 伸平	Shimpei Otake

### m slipped into wikipedia too

wikipedia_en: jsonl/wikipedia_en.jsonl:{"kaki": "新保 海鈴", "yomi": "しmぼ かいlい", "authenticity": "real", "lifetime": {"birth_year": 2002, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Kaili Shimbo", "tags": ["xx-romaji", "masc"]}
 maybe map (vowel)mb or mp to n

### oya? should be ooya.

jsonl/wikipedia_en.jsonl:{"kaki": "大矢 歩", "yomi": "おや あゆみ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Ayumi Oya", "tags": ["xx-romaji", "fem"]}

## KENTARO!!

 {{nihongo|'''Kentaro Shiga'''|志賀 賢太郎|Shiga Kentaro}}

- specifically test 'Kota Ohashi' which used to be おはし　こた. Should be
  おおはし　こうた.
   one way to support this is for romajidb to generate all the possible
   romaji forms, e.g. 後藤（ごとう）generates goto, gotou, gotoh, goto(macron).

## seijiyama import

* Basic import is done.
* Need to remove duplicates with no gender info.
* potentially could scrape gender info - namegen.jp clearly did this as it has
  a male entry for 夏希.

### RomajiDB improvement

 - adding all readings (not just 'best') for split purposes [DONE]
   - maybe mark frequencies? so we can pick the most likely split
 - handle kana
   - kata -> kana
   - whole kana can be skipped since the romaji library handles it, but
     harmless to leave in

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

[**] Also need a re-run for katakana handling update.

### Unambiguous romaji

Technically 'masaya' is unambiguous. 'shinya' etc. are generally
fine, it's mostly u, o and e. Then again, the fallback handles
this, but currently our conversion is 'all or nothing', it does not
treat mei/sei seperately.

### All or nothing

 e.g. 後藤 幸織

 - DEBUG:root:Parsing ('', '常喜儒彦', 'Michihiko Jogi')
 - here if michihiko fails but jogi matches, that should be enough to
   carry out partial conversion, so we at least get 'jougi' right
   and michihiko is probably fine too.

## Make romaji_to_hiragana_fullname swap names for you

This would simplify logic in both researchmap and wikidata_nokana.

### dict tag

Indicates the item should not be counted as a person, it's only for dictionary
completeness. To be implemented in the final database code.

 ... in gender, it should contribute, as it usually is supplementary to
     an item with no gender.
`
1. Replace romaji_to_hiragana, and indicate romaji with xx-romaji tag [DONE]

- scripts/parse_wikidata_nokana.py   -> made messy [change later]
- yomikun/custom_data/importer.py -> made strict
- yomikun/gender/dict.py -> just for debugging
- yomikun/jmnedict/**init**.py -> made strict [need to test!]
- yomikun/researchmap.py -> uses messy [change later]
- yomikun/wikipedia_en/parser.py -> added [change later]

2. Build new database from this  [DONE]
3. Use new database in romaji_to_hiragana  [DONE]
4. Re-enable researchmap tests  [DONE]
5. Run researchmap properly ... doing

- may need to add more stuff to custom.csv
  ... hmm but this will combine with research map to make names seem
  more popular. maybe we can tag stuff in custom.csv so it can be
  removed at dedupe time. e.g. 'dict' tag. then it will be treated
  like jamdict.
- check other error fields.

- check イ トモヒロ     井 智弘 Tomohiro I

6. Can re-run wikipedia-en with better romaji conversion later.

e.g. this one is wrong:


- requires splitting support
- need to keep an eye that we aren't bulldozing well-formed stuff,
  though.
- TODO if we see macrons, should probably ensure the final result
  matches the macron length (e.g. o-bar is exactly 2)

## 'People' counting

Bare name components from researchmap and custom should be counted as
people. Only jmnedict and myoji-yurai should be ignored here.

### xx-split

Do the same with xx-split: mark algorithmically split names so we don't
use that data to do further splitting.

- low priority - not many false positives there

## Researchmap

Once romaji -> kana conversion is done, can finish off import data.
Need to expand into two parts for anonymnity.

## Retrain gender detection

With more data, retrain gender detection. Possibly include 'last two
kana'.

## Rebuild wikipedia EN

Double check no double dashes ('') in names.

## Final database

Person counting: the 'person' tag / person readings need to be split
into kaki/yomi. We can assume any tagged (given/masc/fem/surname)
reading is a real person unless it comes from JMnedict or myoji.

- deduplicates people from people records
- expands subreadings
- fixes lifetime, tags in subreading
- convert yomi to hiragana, rejecting anything non-kana
- strip tags from jmnedict
- Somehow integrate gender data.
