## Romaji to kana conversion

1) Replace romaji_to_hiragana, and indicate romaji with xx-romaji tag
2) Build new database from this
3) Use new database in romaji_to_hiragana: more coverage, frequency
   data so we can prefer one reading over the other.
4) Re-enable researchmap tests
5) Run researchmap properly.
 - may need to add more stuff to custom.csv
   ... hmm but this will combine with research map to make names seem
       more popular. maybe we can tag stuff in custom.csv so it can be
       removed at dedupe time. e.g. 'dict' tag. then it will be treated
       like jamdict.
 - check other error fields.

6) Can re-run wikipedia-en with better romaji conversion later.
  - need to keep an eye that we aren't bulldozing well-formed stuff,
    though.
  - TODO if we see macrons, should probably ensure the final result
    matches the macron length (e.g. o-bar is exactly 2)


### xx-split

Do the same with xx-split: mark algorithmically split names so we don't
use that data to do further splitting.

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