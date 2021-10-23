## Actual current task

 - Generate test database in zipped jsonl format for inclusion into
   the test flutter app.

## Current task

 - extracting gender/dob from seijiyama (done)
  -> join into results, generate anonymised JSONL (done)
  -> remove exact-name duplicates, preserving card info
     confirm: 三河 明史 (3 records, one card info - m)
     三沢 公雄 (3 records, no card info)
     三次 由梨香 (2 records, one card info - f/1992)

 - There are some bogus 2021 values (due to missing DOB data) that should
   be ignored.

 - Ignore entries with no kana


 - reruns: wikipedia_en, _ja, wikidata (?) etc. ja parser has new categories for women.
   wikidata has bracket stripping. wikidata+wiki_en have romaji improvements.

## Basic app!

Let's make a simple app with test data yeah.

## Pitch accents?

Do we have data for common names?

## Random observation

https://en.wikipedia.org/wiki/Kaori\_Manabe
We didn't parse this? We got the other two versions though. In particular,
a crude romajification would lose the を!

https://ja.wikipedia.org/wiki/%E5%B1%B1%E8%88%A9%E6%99%83%E5%A4%AA%E9%83%8E
 - is new, so we son't have it .parsed okay.

## koujien

Fails to split in some places, could be fixed by using RomajiDB

## Gender issues

```
{"kaki": "侑毅", "yomi": "ゆうき", "ml_score": -2.9185547828674316, "ct_score": -0.4463276836158192, "ct_confidence": 0.5115697437195134, "final_score": -0.4463276836158192, "hits_male": 0, "hits_female": 0, "hits_unknown": 1, "err": null}
```
 
Why is the final score based on 1 unknown hit? Should be using ml\_score?

### seijiyama import

* Basic import is done.
* Need to remove duplicates with no gender info.

- Scraping gender info atm. This produces a mapping of card_url -> data
  which can be reintegrated into the seijiyama import somehow.
    - we only do one fetch per name, we could do more.
    - we ignore things with hits > 5 for now
    - obviously a big male bias.

### Observations

For some names (ゆうき・ゆき) perhaps we shouldn't even generate records, as they
would bias the stats? Picking randomly doesn't work either if it's gender-based.

For example ochi/大内 has two readings おおち、おうち, clearly either of them is better
than returning おち!

46 entries for 純一・じゅん which are clearly wrong. Similarly 賢一・けん etc.

Fun stuff here (17 hits):
    "kaki": "京子",
    "yomi": "きようこ",

    "kaki": "純一",
    "yomi": "じゆんいち",

Oh boy...

    "kaki": "淳一",
    "yomi": "じゆんいち",

    "kaki": "亮",
    "yomi": "りよう",

From wikipedia and also researchmap:
jsonl/researchmap.jsonl:{"kaki": "吉田 亮", "yomi": "よしだ りよう", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "researchmap", "tags": ["person"]}
For 'ryou', 274 of these vs. 8830 total. So not too bad. But annoying.

### oya? should be ooya.

jsonl/wikipedia_en.jsonl:{"kaki": "大矢 歩", "yomi": "おや あゆみ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Ayumi Oya", "tags": ["xx-romaji", "fem"]}

5	ohyama, 大山 - failed to convert? similarly kohyama 神山

## KENTARO!!

 {{nihongo|'''Kentaro Shiga'''|志賀 賢太郎|Shiga Kentaro}}

- should use the same logic as research map, much easier. Maybe with a "do not reverse"
  option.
- We were skipping this guy due to requiring >4 template parts. Probably more work to be done there e.g. work out how many we're rejecting.

- specifically test 'Kota Ohashi' which used to be おはし　こた. Should be
  おおはし　こうた.
   one way to support this is for romajidb to generate all the possible
   romaji forms, e.g. 後藤（ごとう）generates goto, gotou, gotoh, goto(macron).

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

Some records make no sense and could be rejected, e.g.
jsonl/wikidata.jsonl:{"kaki": "河野悠里", "yomi": "だいぜんじ ふみこ", "authenticity": "real", "lifetime": {"birth_year": 1983, "death_year": null}, "subreadings": [], "source": "wikidata:http://www.wikidata.org/entity/Q11554202", "tags": ["fem"]}

[**] Also need a re-run for katakana handling update.

### All or nothing

Could tag individual parts of the name with xx-romaji if we had dictionary
data for some but not all?
 - would work if individual scripts output the name part records,
   rather than doing it later.

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
