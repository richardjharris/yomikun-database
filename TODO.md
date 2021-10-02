## TODO List

 - don't think romaji name conversion handles stuff like
   Yu -> Yuu, needs a think.
 - researchamp

- some double dashes still (4 in wikipedia\_en.jsonl)
 - rebuild after testing

Aggregates the generated JSONL data files to make them easier to work with.

- deduplicates people from people records
- expands subreadings
- fixes lifetime, tags in subreading
- convert yomi to hiragana, rejecting anything non-kana
- strip tags from jmnedict

- (maybe) expand people records into parts, preserving gender, lifetime,
  etc. No reason to do this yet though.

The generated data is used as input to both the Gender Prediction code
and the final name database.

- Database preparation:

  - Consolidate JSONL to single file
    - Dedupe people [retain tags/lifetimes]
    - Fix tags
    - Expand subreadings
    - Include gender data?
  - Person dedupe should be done in a way that can be re-used by
    gender code.

- Gender: generate gender dictionary and integrate it somehow

  - use ML only where we are unsure
  - ML may want to include birth year.
  - Have to rebuild first

- Remove subreadings system, replace with list[NameData]

  - simplifies import

- Force 'person' tag instead of adding it later.

- Remove gender tags from JMnedict data as it is usually incorrect.
  Then we can remove the special casing from gender/**init**.py

- Basic flutter app...

### Later stuff

- Reduce db size (e.g. save as json.gz and convert to sqlite later)
- Map names back to sources
- Flutter app
- MeCab, etc.
- ResearchGate - parser works, just needs swapping last/first names around
- https://48pedia.org/%E5%85%A8%E3%83%A1%E3%83%B3%E3%83%90%E3%83%BC%E3%81%AE%E4%B8%80%E8%A6%A7#AKB48

- Other {{nihongo}} references in EN wikipedia?

## From book

上村には「かみむら」と「うえむら」の読みがある。
山崎は「やまざき」と読むのが普通なので、「やまさき」と読んで欲しいと思う人は「ヤマザキではなくヤマサキです」といった注意書きを付けておいたほうがいいという。
「太田」ではなく「大田」という名前のヒットは、「太い「太田」ではなく、大きい「大田」です」という？

rjh@ryzen:~/yomikun/database$ fgrep '"上村 ' jsonl/\* | fgrep -c かみむら
125
rjh@ryzen:~/yomikun/database$ fgrep '"上村 ' jsonl/\* | fgrep -c うえむら
168
rjh@ryzen:~/yomikun/database$ fgrep '"山崎 ' jsonl/\* | fgrep -c やまさき
217
rjh@ryzen:~/yomikun/database$ fgrep '"山崎 ' jsonl/\* | fgrep -c やまざき
928

### JA Wikipedia

# 士郎 正宗

Pen name according to wiki-en, but we reported 'real'.
To fix this we'd need to use wikidata to collect interlanguage links, to notice
that all the records are for the same person.

### EN Wikipedia

# https://en.wikipedia.org/wiki/Shingo\_Tano

Born name in infobox.
