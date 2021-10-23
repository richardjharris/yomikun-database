## Sort of current task

 - Generate test database in zipped jsonl format
 - Make Flutter app load it
 - Make Flutter app use it

## Current task

Rebuilding all data, checking each step

 - rebuild gender/romaji dictionaries. check 'dict' tag!
  - rebuild genderdb
    - need to identify final_score (doing...)
  - rebuild romajidb

  - final database build

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

### oya? should be ooya.

jsonl/wikipedia_en.jsonl:{"kaki": "大矢 歩", "yomi": "おや あゆみ", "authenticity": "real", "lifetime": {"birth_year": 1994, "death_year": null}, "subreadings": [], "source": "wikipedia_en:Ayumi Oya", "tags": ["xx-romaji", "fem"]}
5	ohyama, 大山 - failed to convert? similarly kohyama 神山

### Kota Ohashi

- 'Kota Ohashi' was おはし　こた. Should be  おおはし　こうた.

- Recently おおあし こた ... that's not any better !!

- This is hard to fix, but we're definitely doing something wrong with
  ohashi here.

## Final database

We count everyone except for 'dict'

- deduplicates people from people records (done)
- expands subreadings (?)
- fixes lifetime, tags in subreading (?)
- convert yomi to hiragana, rejecting anything non-kana (this is done earlier)
- Somehow integrate gender data.

## Minor issues with 'notes'

{"kaki": "広瀬 茂男", "yomi": "ひろせ しげお", "authenticity": "real", "lifetime": {"birth_year": 1947, "death_year": null}, "source": "wikipedia_en:Shigeo Hirose", "tags": ["xx-romaji", "masc", "person"], "notes": "Pioneer of robotics technology BBC NEWS | In pictures: Robot menagerie, Robot lab    and a professor at the Tokyo Institute of Technology"}
{"kaki": "垣越 建伸", "yomi": "かきこし けんしん", "authenticity": "real", "lifetime": {"birth_year": 2000, "death_year": null}, "source": "wikipedia_en:Kenshin Kakikoshi", "tags": ["xx-romaji", "masc", "person"], "notes": "People|Japanese] professional [baseball pitcher for the Chunichi Dragons of Nippon Professional Baseball (NPB)"}

Could be fixed by making custom.csv preferred, and defining proper notes there.
Would also solve the xx-romaji issue.
Speaking of, we can definitely remove xx-romaji if we find matching non-xx-romaji entries
for the same person.