## Current task

Building an SQLite database good enough to use with the app, ideally
in 100MB or less.

 - convert ml\_score to 1 byte (not 8)
 - remove top5k
 - add back birth years etc.

Enable compression: gzipping the sqlite file shrinks it from 45M or 13M
 - bz2 and xz are even better
 - size is comparable to the gzipped JSONL, and faster to load.

Removing indexes helps a bit (10M less uncompressed) but would prevent us
from using the database as read-only, which is currently required for web.
On the other hand, a web version would probably use an API for the database
anyway.

 - Make Flutter app load it
 - Make Flutter app use it

 - At some point, add 'people' too.

---

## Use the Researchmap code in all importers

ENwiki, wikidata etc. should use the same Researchmap code that already
handles clever stuff.

 namedata, err = intuit_name_data(kana, kanji, romaji)

{"kaki": "奥田 教介", "yomi": "おくだ きょすけ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "source": "wikidata:http://www.wikidata.org/entity/Q106392717", "tags": ["xx-romaji", "masc", "person"]}

^ this for example.

### Related: make romaji_to_hiragana_fullname swap names for you

This would simplify logic in both researchmap and wikidata_nokana.

### koujien

Fails to split in some places, could be fixed by using RomajiDB

### Kentaro

 {{nihongo|'''Kentaro Shiga'''|志賀 賢太郎|Shiga Kentaro}}

 ^ we currently do a reverse hack for this
 - researchmap code would negate the need for it.

### oya? should be ooya.

jsonl/wikipedia_en.jsonl:{"kaki": "大矢 歩", "yomi": "おや あゆみ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Ayumi Oya", "tags": ["xx-romaji", "fem"]}
5	ohyama, 大山 - failed to convert? similarly kohyama 神山

### Kota Ohashi

- 'Kota Ohashi' was おはし　こた. Should be  おおはし　こうた.

- Recently おおあし こた ... that's not any better !!

- This is hard to fix, but we're definitely doing something wrong with
  ohashi here.

## Minor issues with 'notes'

{"kaki": "広瀬 茂男", "yomi": "ひろせ しげお", "authenticity": "real", "lifetime": {"birth_year": 1947, "death_year": null}, "source": "wikipedia_en:Shigeo Hirose", "tags": ["xx-romaji", "masc", "person"], "notes": "Pioneer of robotics technology BBC NEWS | In pictures: Robot menagerie, Robot lab    and a professor at the Tokyo Institute of Technology"}
{"kaki": "垣越 建伸", "yomi": "かきこし けんしん", "authenticity": "real", "lifetime": {"birth_year": 2000, "death_year": null}, "source": "wikipedia_en:Kenshin Kakikoshi", "tags": ["xx-romaji", "masc", "person"], "notes": "People|Japanese] professional [baseball pitcher for the Chunichi Dragons of Nippon Professional Baseball (NPB)"}

Could be fixed by making custom.csv preferred, and defining proper notes there.
Would also solve the xx-romaji issue.
Speaking of, we can definitely remove xx-romaji if we find matching non-xx-romaji entries
for the same person.
