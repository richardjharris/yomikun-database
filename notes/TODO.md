## Current task

Expand the sqlite database, adding:
 - first and last year seen for names
 - people table (list of notable people) maybe. might be too big.
 - myoji_yurai table for top5k names, ranks and popcounts

 - Loader needs to support all of this.

Current process:
 - db/deduped.json is deduped people + other records
 - db/gender.json genderated from above
 - db/final.json takes deduped and converts to sqlite schema
 - db/final.db loads json into sqlite

# Also (app)

 - kanji with most kana
 - kana with most kanji
 - relative to total (e.g. names with readings/kanji that account for 50% or something)
 - ignoring '0' results
