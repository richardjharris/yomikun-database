## TODO List

 - Gender stats + more detailed information

 - EN wikipedia FPs etc. (below)
 - Could log names as given/male/female/surname/unclas but this
   complicates matters a bit? But allows us to see count of sightings.
   Perhaps attaching gender to Person is easier?

 - Fix ja tests, which now need genders added.

 - Person de-duping / merging birth/death data
 - Remove subreadings system, replace with list[NameData]
   - simplifies import

### Later stuff

 - Reduce db size (e.g. save as json.gz and convert to sqlite later)
 - Map names back to sources
 - Flutter app
 - MeCab, etc.

### EN Wikipedia

# Fictional but we should include? Possibly.
{"kaki": "不知火 舞", "yomi": "しらぬい まい", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Mai Shiranui", "tags": ["fem"]}

# rare case where we did not split. see yomi ''
{"kaki": "玉椿憲太郎", "yomi": "''たまつばき けんたろう''", "authenticity": "real", "lifetime": {"birth_year": 1883, "death_year": 1928}, "subreadings": [], "source": "wikipedia_en:Tamatsubaki Kentarō", "tags": ["masc"]}

# not a name
{"kaki": "拡張新字体", "yomi": "かくちょう しんじたい", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Extended shinjitai", "tags": []}

# fictional? no dates
{"kaki": "亜馬尻 菊の助", "yomi": "あばしり きくのすけ", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "wikipedia_en:The Abashiri Family", "tags": ["fem"]}

{"kaki": "艦隊これくしょん", "yomi": "かんたい これくしょん", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Kantai Collection (TV series)", "tags": ["fem"]}

{"kaki": "楽しんご", "yomi": "たの しんご", "authenticity": "real", "lifetime": {"birth_year": 1979, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Shingo Tano", "tags": ["masc"]}

# vvv
{"kaki": "太田正典", "yomi": "ōた まさのり", "authenticity": "real", "lifetime": {"birth_year": 1961, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Masamune Shirow", "tags": ["masc"]}
 -> error in kana

Minoru_Yamasaki -> no gender

## Observations (lower priority)

wikipedia_ja.jsonl:{"kaki": "藤原 伊子", "yomi": "ふじわら の", "authenticity": "real", "lifetime": {"birth_year": 1167, "death_year": null}, "subreadings": [], "source": "wikipedia_ja:藤原伊子", "tags": []}

 ^ reading 'iko' is obviously missing too.

の in the middle of the name:
源 頼家（みなもと の よりいえ）は、鎌倉時代前期の鎌倉幕府第2代将軍（鎌倉殿）。鎌倉幕府を開いた源頼朝の嫡男で母は北条政子（頼朝の子としては第3子で次男、政子の子としては第2子で長男）。

Chinese names: https://ja.m.wikipedia.org/wiki/%E4%BA%8E%E5%90%89 
  These could be tagged

FP ish:
{"kaki": "坪田 愛華", "yomi": "つぼた あいか", "authenticity": "real", "lifetime": {"birth_year": 1979, "death_year": 1991}, "subreadings": [], "source": "wikipedia_ja:地球の秘密"}

How the heck did it extract this name? Looks like infobox as part of an article about something else!
Therefore TODO we need to check the names are the same before
 copying information!

A few pages have >1 honmyo:
https://ja.m.wikipedia.org/wiki/%E5%9C%B0%E7%90%83_(%E3%81%8A%E7%AC%91%E3%81%84%E3%82%B3%E3%83%B3%E3%83%93)

{"kaki": "足利将軍一覧 足利将軍一覧", "yomi": "あしかがしょうぐん いちらん", "authenticity": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": []}

Sometimes hiragana comes first, this is a fairly common pattern for mangaka.

'''たがみ よしひさ'''（本名：田上 喜久<ref name="duo">[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983年7月1日、朝日ソノラマ、p.236</ref><ref name="wolf">プレイコミックシリーズ版『我が名は狼』全 3 巻（1982 年 - 1983 年）の折り返し部分に、著者近影とともにプロフィールが記載されている。</ref>、[[1958年]][[12月9日]]<ref name="duo" /><ref name="wolf" /> - ）は、[[日本]]の[[漫画家]]。代表作に『[[軽井沢シンドローム]]』など。同じく漫画家の[[小山田いく]]は実兄<ref>[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983 年 7 月 1 日、朝日ソノラマ、p.236</ref><ref>[[秋田書店]]『我が名は狼』プレイコミックシリーズ版全 3 巻（1982 年 - 1983 年）の折り返し部分、'''たがみよしひさ'''のプロフィール参照。</ref>。

かわぐち かいじ（本名：川口 開治、1948年7月27日 - ）は、日本の漫画家。 <- same deal
