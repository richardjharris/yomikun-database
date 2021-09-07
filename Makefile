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

JSONLFILES = koujien.jsonl daijisen.jsonl pdd.jsonl wikipedia_ja.jsonl jmnedict.jsonl myoji-yurai.jsonl wikipedia_en.jsonl

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

wikipedia_en.jsonl: data/enwiki-nihongo-articles.gz
	pzcat data/enwiki-nihongo-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_en.py > $@

wikipedia_ja.jsonl: data/jawiki-articles.gz
	pzcat data/jawiki-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_ja.py > $@

jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@

myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	python scripts/parse_myoji_yurai.py < $^ > $@

koujien.jsonl: data/koujien.json.gz
	zcat $< | python scripts/parse_koujien.py > $@

daijisen.jsonl: data/daijisen.json.gz
	zcat $< | python scripts/parse_daijisen.py > $@

pdd.jsonl: data/pdd.json.gz
	zcat $< | python scripts/parse_pdd.py > $@