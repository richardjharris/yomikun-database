### TODO

 - Possibly having a single type field (surname/given/male/female/unclass) like jmnedict
   is easier than having two fields, as surname + gender makes no sense anyway
   Then we can remove tags?
   Then we can output a single row for each name type, which simplifies processing later.

 - Database is 50MB. Problem?
 - Consider a way to mapping names back to sources.

## JP wikipedia

{"kaki": "太田正典", "yomi": "ōた まさのり", "authenticity": "real", "lifetime": {"birth_year": 1961, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Masamune Shirow", "tags": ["masc"]}
 -> error in kana

Minoru_Yamasaki -> no gender

## Later todo

 - Basic flutter app
 - Import names from MeCab?
 - Import names from mtk dict etc.

## Observations (lower priority)

 - consider ignoring before we do further processing (such as name splits)

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

Possible for readings to contain katakana, although this seems mostly
for mangaka names, e.g.

'''羽海野 チカ'''（うみの チカ、8 月 30 日生<ref name="Profile">[http://natalie.mu/comic/artist/1800 コミックナタリー羽海野チカ]（2011 年 7 月 29 日閲覧）</ref>）は、[[日本]]の[[漫画家]]。[[東京都]][[足立区]]出身<ref name="Profile" />。[[東京都立工芸高等学校]]<ref>

'''中崎 タツヤ'''（なかざき タツヤ、[[1955年]][[8月11日]] - ）は、[[日本]]の[[漫画家]]。[[愛媛県]][[西予市]]生まれ、[[愛知県]]育ち。[[名古屋市立工芸高等学校]]卒業。

'''永田 トマト'''（ながた トマト、[[1959年]]<ref name="yb">『YOUNG BLOOD』第 1 巻 表 3 小学館</ref> - ）は[[日本]]の[[漫画家]]。[[静岡県]][[静岡市]]出身<ref name="yb" />。

Sometimes hiragana comes first, this is a fairly common pattern for mangaka.

'''たがみ よしひさ'''（本名：田上 喜久<ref name="duo">[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983年7月1日、朝日ソノラマ、p.236</ref><ref name="wolf">プレイコミックシリーズ版『我が名は狼』全 3 巻（1982 年 - 1983 年）の折り返し部分に、著者近影とともにプロフィールが記載されている。</ref>、[[1958年]][[12月9日]]<ref name="duo" /><ref name="wolf" /> - ）は、[[日本]]の[[漫画家]]。代表作に『[[軽井沢シンドローム]]』など。同じく漫画家の[[小山田いく]]は実兄<ref>[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983 年 7 月 1 日、朝日ソノラマ、p.236</ref><ref>[[秋田書店]]『我が名は狼』プレイコミックシリーズ版全 3 巻（1982 年 - 1983 年）の折り返し部分、'''たがみよしひさ'''のプロフィール参照。</ref>。

かわぐち かいじ（本名：川口 開治、1948 年 7 月 27 日 - ）は、日本の漫画家。 <- same deal
