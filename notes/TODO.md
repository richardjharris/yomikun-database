## Current task

Expand the sqlite database, adding:
 - first and last year seen for names
 - people table (list of notable people) maybe. might be too big.
 - myoji_yurai table for top5k names, ranks and popcounts

 - Loader needs to support all of this.

# Also (app)

 - kanji with most kana
 - kana with most kanji
 - relative to total (e.g. names with readings/kanji that account for 50% or something)
 - ignoring '0' results

## Use the Researchmap code in all importers

Wikidata etc. should use the same researchmap code that already
handles clever stuff.

 namedata, err = intuit_name_data(kana, kanji, romaji)

{"kaki": "奥田 教介", "yomi": "おくだ きょすけ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "source": "wikidata:http://www.wikidata.org/entity/Q106392717", "tags": ["xx-romaji", "masc", "person"]}

^ this for example.

### Related: make romaji_to_hiragana_fullname swap names for you

This would simplify logic in both researchmap and wikidata_nokana.

### koujien

Fails to split in some places, could be fixed by using RomajiDB