## Romaji to kana conversion

Current task: finish researchmap import [DONE]
 - maybe look at the 'messy conversions' and add custom.csv entries.

Edge cases involving h:
 yuhya (裕也) didn't pass. (hirahara yuhya, 平原 裕也)

(maki nahomi, 牧 奈歩美) - this is nahomi

DEBUG:root:[rom->hira] input(Ohishi, 大石, Sei, ohishi) match(おおいし, oishi) => False`
otoh 'Ohashi' DOES need converting to oohashi.
and 'Ohira' is oohira.
and 'tomohiro' is never 'tomouiro'
but オオイ ヒロシ   大井 洋 Hiroshi Ohi

 - could special case ohi, ohishi, ohiwa, ohike, ohizumi
   ohe... ohuchi, ohue, ohura

## wikidata: ・

There are quite a few names with ・ instead of a space.
 "小原宏裕", "yomi": "おはら・こうゆう"

### Unambiguous romaji

Technically 'masaya' is unambiguous. 'shinya' etc. are generally
fine, it's mostly u, o and e. Then again, the fallback handles
this, but currently our conversion is 'all or nothing', it does not
treat mei/sei seperately.

### All or nothing

 - DEBUG:root:Parsing ('', '常喜儒彦', 'Michihiko Jogi')
 - here if michihiko fails but jogi matches, that should be enough to
   carry out partial conversion, so we at least get 'jougi' right
   and michihiko is probably fine too.

## Make romaji_to_hiragana_fullname swap names for you

This would simplify logic in both researchmap and wikidata_nokana.

### dict tag

Indicates the item should not be counted as a person, it's only for dictionary
completeness. To be implemented in the final database code.
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

- requires splitting support
- need to keep an eye that we aren't bulldozing well-formed stuff,
  though.
- TODO if we see macrons, should probably ensure the final result
  matches the macron length (e.g. o-bar is exactly 2)
- specifically test 'Kota Ohashi' which used to be おはし　こた. Should be
  おおはし　こうた.

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
