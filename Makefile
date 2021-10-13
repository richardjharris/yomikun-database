export PYTHONPATH := ${PYTHONPATH}:.
export TMPDIR = ./tmp

SHELL = /bin/bash -o pipefail

mproc ?= 8

ifeq ($(mproc),1)
  PARALLEL=
else
  PARALLEL=parallel --will-cite --gnu -k --pipe -j $(mproc) --tmpdir $(TMPDIR)
endif

ZCAT = scripts/pzcat

export ROMAJIDB_TSV_PATH = foo

.DELETE_ON_ERROR:

.PHONY: all clean test

JSONL = koujien daijisen pdd jmnedict myoji-yurai wikipedia_en wikipedia_ja wikidata wikidata-nokana custom researchmap
JSONLFILES = $(JSONL:%=jsonl/%.jsonl)

db/gender.jsonl db/gender.weights &: db/people.jsonl data/name_lists.json
	cat db/people.jsonl | python scripts/build_gender_db.py > db/gender.jsonl

db/names.sqlite: ${JSONLFILES} db/people.jsonl
	cat $^ | python scripts/load_data.py $@

clean:
	rm -f ${JSONLFILES}
	rm -f db/people.jsonl db/names.sqlite

test:
	pytest

db/people.jsonl: ${JSONLFILES}
	cat $^ | python scripts/person_dedupe.py > $@

# We pre-filter the wikipedia XML dump for articles likely to be Japanese names
# and also convert the XML to JSON. Takes ~2 hours.
data/enwiki-nihongo-articles.gz: |data/enwiki.xml.bz2
	bzcat data/enwiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl |\
	  fgrep -e '{{Nihongo' -e '{{nihongo' -e 'Japanese' -e 'japanese' | gzip -9f > $@

data/jawiki-articles.gz: |data/jawiki.xml.bz2
	bzcat data/jawiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl | gzip -9f > $@

# Generated from whatever JSON files are available. Should be rebuilt periodically.
data/romajidb.tsv.gz:
	cat jsonl/* | python scripts/build_romajidb.py | gzip -9f > $@

jsonl/wikipedia_en.jsonl: data/enwiki-nihongo-articles.gz
	${ZCAT} data/enwiki-nihongo-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_en.py > $@

jsonl/wikipedia_ja.jsonl: data/jawiki-articles.gz
	${ZCAT} data/jawiki-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_ja.py > $@

jsonl/wikidata.jsonl: data/wikidata.jsonl.gz
	${ZCAT} $< | ${PARALLEL} python scripts/parse_wikidata.py > $@ 2>/dev/null

jsonl/wikidata-nokana.jsonl: data/wikidata-nokana.jsonl.gz
	${ZCAT} $< | ${PARALELL} python scripts/parse_wikidata_nokana.py > $@

jsonl/custom.jsonl: data/custom.csv
	python scripts/parse_custom_data.py < $< > $@

data/researchmap.jsonl:
	${ZCAT} data/researchmap.gz | python scripts/import_researchmap.py > $@

jsonl/researchmap.jsonl: data/researchmap.jsonl
	cp $^ $@

jsonl/jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@

jsonl/myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	python scripts/parse_myoji_yurai.py < $^ > $@

jsonl/koujien.jsonl: data/koujien.json.gz
	zcat $< | python scripts/parse_koujien.py > $@

jsonl/daijisen.jsonl: data/daijisen.json.gz
	zcat $< | python scripts/parse_daijisen.py > $@

jsonl/pdd.jsonl: data/pdd.json.gz
	zcat $< | python scripts/parse_pdd.py > $@
