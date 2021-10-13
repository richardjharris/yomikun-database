## Romaji to kana conversion

 ADD RomajiDB to romaji_fullname converter.

Edge case here:

`DEBUG:root:[rom->hira] input(Ohishi, 大石, Sei, ohishi) match(おおいし, oishi) => False`
otoh 'Ohashi' DOES need converting to oohashi.

- Masahiro Ohashi (大橋 正博
- OTOH very minor. 32k entries have xx-romaji, most of which are correct.

{"kaki": "大橋 滉太", "yomi": "おはし こた", "authenticity": "real", "lifetime": {"birth_year": 2002, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Kota Ohashi", "tags": ["xx-romaji"]}

- double mistake here, should be おおはし　こうた

吉田 有希 could be read yuki (fem) or yuuki (masc or fem?)

1. Replace romaji_to_hiragana, and indicate romaji with xx-romaji tag

- scripts/parse_wikidata_nokana.py   -> made messy [change later]
- yomikun/custom_data/importer.py -> made strict
- yomikun/gender/dict.py -> just for debugging
- yomikun/jmnedict/**init**.py -> made strict [need to test!]
- yomikun/researchmap.py -> uses messy [change later]
- yomikun/wikipedia_en/parser.py -> added [change later]

2. Build new database from this
3. Use new database in romaji_to_hiragana: more coverage, frequency
   data so we can prefer one reading over the other.
4. Re-enable researchmap tests
5. Run researchmap properly.

- may need to add more stuff to custom.csv
  ... hmm but this will combine with research map to make names seem
  more popular. maybe we can tag stuff in custom.csv so it can be
  removed at dedupe time. e.g. 'dict' tag. then it will be treated
  like jamdict.
- check other error fields.

6. Can re-run wikipedia-en with better romaji conversion later.

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
