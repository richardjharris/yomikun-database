export PYTHONPATH := ${PYTHONPATH}:.
export TMPDIR = ./tmp
export SHELL = bash -o pipefail

mproc ?= 8

ifeq ($(mproc),1)
  PARALLEL=
else
  PARALLEL=parallel --will-cite --gnu -k --pipe -j $(mproc) --tmpdir $(TMPDIR)
endif

.DELETE_ON_ERROR:

.PHONY: all clean test

JSONL = koujien daijisen pdd jmnedict myoji-yurai wikipedia_en wikipedia_ja wikidata wikidata-nokana custom
JSONLFILES = $(JSONL:%=jsonl/%.jsonl)

names.sqlite: ${JSONLFILES}
	cat $^ | python scripts/load_data.py $@

clean:
	rm -f ${JSONLFILES}
	rm -f names.sqlite

test:
	pytest

# We pre-filter the wikipedia XML dump for articles likely to be Japanese names
# and also convert the XML to JSON. Takes ~2 hours.
data/enwiki-nihongo-articles.gz: |data/enwiki.xml.bz2
	bzcat data/enwiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl |\
	  fgrep -e '{{Nihongo' -e '{{nihongo' -e 'Japanese' -e 'japanese' | pigz -9f > $@

data/jawiki-articles.gz: |data/jawiki.xml.bz2
	bzcat data/jawiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl | pigz -9f > $@

jsonl/wikipedia_en.jsonl: data/enwiki-nihongo-articles.gz
	pzcat data/enwiki-nihongo-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_en.py > $@

jsonl/wikipedia_ja.jsonl: data/jawiki-articles.gz
	pzcat data/jawiki-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_ja.py > $@

jsonl/wikidata.jsonl: data/wikidata.jsonl.gz
	pzcat $< | ${PARALLEL} python scripts/parse_wikidata.py > $@ 2>/dev/null

jsonl/wikidata-nokana.jsonl: data/wikidata-nokana.jsonl.gz
	pzcat $< | ${PARALELL} python scripts/parse_wikidata_nokana.py > $@

jsonl/custom.jsonl: data/custom.yaml
	python scripts/parse_custom_yaml.py < $< > $@

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