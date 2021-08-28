### TODO

 - Wikipedia filtering: long names, gakkou
  {"kaki": "道の駅米沢 道の駅米沢", "yomi": "みちのえき よねざわ", "name_type": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": []}
   - why does this appear twice?? some bad attempt at splitting it.

 - Use empty NameData instead of NameData|None everywhere.

 - Add importer for the top 5000 list - this identifies the 'official'
   readings for those names.

 - MERGE process -> sqlite
  - each dictionary returns a set of (kaki, yomi, type, lifetime)

  How to do it?
   * import all names into a database (kanji, reading, part: forename, surname) including gender info
     full name matches can be left as-is i guess

   * for each data source
     - add any missing first/last names to the database
     - add full name entries
     - add a reference for both name parts (e.g. forename -> REF)
    
   * compute the relative score for each name
     - e.g. for each kanji, find all readings and all references to each reading
     - figure out a score

 - Basic flutter app

---

の in the middle of the name:
源 頼家（みなもと の よりいえ）は、鎌倉時代前期の鎌倉幕府第2代将軍（鎌倉殿）。鎌倉幕府を開いた源頼朝の嫡男で母は北条政子（頼朝の子としては第3子で次男、政子の子としては第2子で長男）。

Chinese names: https://ja.m.wikipedia.org/wiki/%E4%BA%8E%E5%90%89 
  These could be tagged

FP:
{"kaki": "公益社団法人応用物理学会 公益社団法人応用物理学会", "yomi": "こうえきしゃだんほうじん おうようぶつりがっか
い", "name_type": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": []}
{"kaki": "足利将軍一覧 足利将軍一覧", "yomi": "あしかがしょうぐん いちらん", "name_type": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": []}

LOL:
{"kaki": "必殺仕置人殺人事件 必殺仕置人殺人事件", "yomi": "ひっさつしおきにん さつじんじけん", "name_type": "real", "lifetime": {"birth_year": null, "death_year": null}, "subreadings": []}


Possible for readings to contain katakana, although this seems mostly
for mangaka names, e.g.

'''羽海野 チカ'''（うみの チカ、8 月 30 日生<ref name="Profile">[http://natalie.mu/comic/artist/1800 コミックナタリー羽海野チカ]（2011 年 7 月 29 日閲覧）</ref>）は、[[日本]]の[[漫画家]]。[[東京都]][[足立区]]出身<ref name="Profile" />。[[東京都立工芸高等学校]]<ref>

'''中崎 タツヤ'''（なかざき タツヤ、[[1955年]][[8月11日]] - ）は、[[日本]]の[[漫画家]]。[[愛媛県]][[西予市]]生まれ、[[愛知県]]育ち。[[名古屋市立工芸高等学校]]卒業。

'''永田 トマト'''（ながた トマト、[[1959年]]<ref name="yb">『YOUNG BLOOD』第 1 巻 表 3 小学館</ref> - ）は[[日本]]の[[漫画家]]。[[静岡県]][[静岡市]]出身<ref name="yb" />。

Katakana here:

'''二ノ宮 知子'''（にのみや ともこ、[[1969年]][[5月25日]] - ）は、[[日本]]の[[漫画家]]。[[埼玉県]][[秩父郡]][[皆野町]]出身、埼玉県在住。女性。[[ABO式血液型|血液型]]B 型。
https://ja.wikipedia.org/wiki/%E4%BA%8C%E3%83%8E%E5%AE%AE%E7%9F%A5%E5%AD%90

Sometimes hiragana comes first, this is a fairly common pattern for mangaka.
Watch out because something is autoformatting this markdown in a bad way.

'''たがみ よしひさ'''（本名：田上 喜久<ref name="duo">[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983年7月1日、朝日ソノラマ、p.236</ref><ref name="wolf">プレイコミックシリーズ版『我が名は狼』全 3 巻（1982 年 - 1983 年）の折り返し部分に、著者近影とともにプロフィールが記載されている。</ref>、[[1958年]][[12月9日]]<ref name="duo" /><ref name="wolf" /> - ）は、[[日本]]の[[漫画家]]。代表作に『[[軽井沢シンドローム]]』など。同じく漫画家の[[小山田いく]]は実兄<ref>[[DUO (マンガ雑誌)|デュオ]]別冊『たがみよしひさの世界』、1983 年 7 月 1 日、朝日ソノラマ、p.236</ref><ref>[[秋田書店]]『我が名は狼』プレイコミックシリーズ版全 3 巻（1982 年 - 1983 年）の折り返し部分、'''たがみよしひさ'''のプロフィール参照。</ref>。

かわぐち かいじ（本名：川口 開治、1948 年 7 月 27 日 - ）は、日本の漫画家。 <- same deal
