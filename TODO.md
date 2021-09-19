## TODO List

 - Gender: generate gender dictionary and integrate it somehow
   - use ML only where we are unsure
   - make sure の values are gone (currently 3,872 entries)

 - (^) Person de-duping / merging birth/death data
  - should be done before computing gender stats (?)
  - possibly done in a preparatory step before data import.

 - Remove subreadings system, replace with list[NameData]
   - simplifies import

 - Force 'person' tag instead of adding it later.

 - improve handling of very old names e.g. 
   小野妹子、蘇我馬子、中臣鎌子、 阿部鳥子
    - tweak の handling
    - old names with 妻 entry are probably men.
     ^ 名に「子」の字が付くが男性である（当時は「子」が男女問わず用いられた）。子 (人名)を参照のこと。

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

### JA Wikipedia

# 士郎 正宗
Pen name according to wiki-en, but we reported 'real'.

### EN Wikipedia

# https://en.wikipedia.org/wiki/Shingo_Tano
Born name in infobox.