## TODO List

 - Database preparation:
   - dedupe Person. retain tags/lifetimes
   - collect 

 - Gender: generate gender dictionary and integrate it somehow
   - use ML only where we are unsure
   - ML may want to include birth year.
   - Have to rebuild first

 - (^) Person de-duping / merging birth/death data
  - should be done before computing gender stats (?)
  - possibly done in a preparatory step before data import.

 - Remove subreadings system, replace with list[NameData]
   - simplifies import

 - Force 'person' tag instead of adding it later.

 - Remove gender tags from JMnedict data as it is usually incorrect.
   Then we can remove the special casing from gender/__init__.py

  - maybe names with no spaces? might be chinese
    ones etc.

 『日本書紀』の時代には、小野妹子、蘇我馬子、中臣鎌子（鎌足）、阿部鳥子など、主に男性に子型の名が付いた。

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

rjh@ryzen:~/yomikun/database$ fgrep '"上村 ' jsonl/* | fgrep -c かみむら
125
rjh@ryzen:~/yomikun/database$ fgrep '"上村 ' jsonl/* | fgrep -c うえむら
168
rjh@ryzen:~/yomikun/database$ fgrep '"山崎 ' jsonl/* | fgrep -c やまさき
217
rjh@ryzen:~/yomikun/database$ fgrep '"山崎 ' jsonl/* | fgrep -c やまざき
928

### JA Wikipedia

# 士郎 正宗
Pen name according to wiki-en, but we reported 'real'.

### EN Wikipedia

# https://en.wikipedia.org/wiki/Shingo_Tano
Born name in infobox.