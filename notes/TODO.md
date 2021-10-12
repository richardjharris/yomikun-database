## Romaji to kana conversion

Problem 1) researchmap requires romaji to kana conversion
        2) wikipedia\_en sometimes has incorrect romaji
           (will need a rebuild)

 - need to replace romaji_to_hiragana where relevant
 - pick longest may not be best [pick most frequent / non-JMnedict]
 - add a tag

### Enhancing the data

1. Add a tag anywhere where we performed a romaji conversion and there
   were no macrons. (to avoid dogfooding)
2. Build new name database from our data
3. Tagged items may be used as a last resort, although we should probably
   just error.

## Researchmap

Once romaji -> kana conversion is done, can finish off import data.
Need to expand into two parts for anonymnity.

## Retrain gender detection

With more data, retrain gender detection. Possibly include 'last two
kana'.

## Rebuild wikipedia EN

Double check no double dashes ('') in names.

## Custom data

 - custom.yaml to .jsonl converter (and sanity checker)
   - skip comments, normalise spaces
   - handle tags
   - add person tag if missing

## Final database

Person counting: should be attached to readings, as we won't always
add a Person entry. Basically anything non-jmnedict should be counted
as a person.

- deduplicates people from people records
- expands subreadings
- fixes lifetime, tags in subreading
- convert yomi to hiragana, rejecting anything non-kana
- strip tags from jmnedict

Somehow integrate gender data.