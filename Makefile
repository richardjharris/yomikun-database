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
CAT = pv
YOMIKUN = python scripts/yk.py

# Much faster than bzcat
BZCAT = lbzcat

export ROMAJIDB_TSV_PATH = data/romajidb.tsv.gz

.DELETE_ON_ERROR:

.PHONY: all clean test prep prep-perl deadcode cover lint install

JSONL = koujien daijisen pdd jmnedict myoji-yurai wikipedia_en wikipedia_ja wikidata wikidata-nokana custom researchmap seijiyama
JSONLFILES = $(JSONL:%=jsonl/%.jsonl)

# Installs to the app assets folder for distribution
install: db/final.db
	cp $< ../app/assets/namesdb.sqlite3
	sqlite3 --csv --noheader $< 'pragma user_version' > ../app/assets/namesdb.version.txt 2>/dev/null

db/final.db: db/final.jsonl
	rm -f $@ && $(YOMIKUN) build-sqlite $@ < $<

db/final.jsonl: db/deduped.jsonl
	python scripts/build_final_database.py < $< > $@

db/gender.jsonl: db/deduped.jsonl data/name_lists.json
	python scripts/build_gender_db.py < $< > $@

clean:
	rm -f ${JSONLFILES}
	rm -f db/deduped.jsonl db/final.jsonl

test:
	pytest

cover:
	coverage run -m pytest
	coverage html
	(sleep 1 && xdg-open http://localhost:8111) & python -m http.server --directory htmlcov 8111

prep:
	# Wheel is required for jamdict-data
	pip install wheel
	pip install -r requirements.txt
	# Optional
	pip install coverage vulture

prep-perl:
	cpanm MediaWiki::DumpFile::FastPages JSON::XS

deadcode: vulture-whitelist
	vulture vulture-whitelist

vulture-whitelist:
	-vulture --make-whitelist > $@

lint:
	-pylint scripts yomikun tests/*.py

db/deduped.jsonl: ${JSONLFILES}
	${CAT} $^ | python scripts/person_dedupe.py > $@

# Caution: LARGE! 36GB as of Oct 2021
# Can be replaced with an empty file once data/enwiki-nihongo-articles.gz is built, as you are
# unlikely to need any other articles.
data/enwiki.xml.bz2:
	curl https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-meta-current.xml.bz2 -o $@

# 4.1GB as of Oct 2021
data/jawiki.xml.bz2:
	curl https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-pages-meta-current.xml.bz2 -o $@

# We pre-filter the wikipedia XML dump for articles likely to be Japanese names
# and also convert the XML to JSON. Takes ~1 hour.
# After this, the dump can be deleted (or replaced with an empty file)
data/enwiki-nihongo-articles.gz: data/enwiki.xml.bz2
	${BZCAT} data/enwiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl |\
	  fgrep -e '{{Nihongo' -e '{{nihongo' -e Japanese -e japanese -e Japan -e japan | gzip -9f > $@

# Further filter to match only template uses, as we don't currently support any other
# type of article.
data/enwiki-template-only.gz: data/enwiki-nihongo-articles.gz
	${ZCAT} $< | fgrep -e '{{Nihongo' -e '{{nihongo' | gzip -9f > $@

data/jawiki-articles.gz: data/jawiki.xml.bz2
	${BZCAT} data/jawiki.xml.bz2 | perl scripts/parse_mediawiki_dump_fast.pl | gzip -9f > $@

# Generated from whatever JSON files are available. Should be rebuilt periodically.
data/romajidb.tsv.gz:
	${CAT} jsonl/* | python scripts/build_romajidb.py | gzip -9f > $@

jsonl/wikipedia_en.jsonl: data/enwiki-template-only.gz
	${ZCAT} $< | $(PARALLEL) python scripts/parse_wikipedia_en.py > $@

jsonl/wikipedia_ja.jsonl: data/jawiki-articles.gz
	${ZCAT} data/jawiki-articles.gz | $(PARALLEL) python scripts/parse_wikipedia_ja.py > $@

jsonl/wikidata.jsonl: data/wikidata.jsonl.gz
	${ZCAT} $< | ${PARALLEL} python scripts/parse_wikidata.py > $@ 2>/dev/null

jsonl/wikidata-nokana.jsonl: data/wikidata-nokana.jsonl.gz
	${ZCAT} $< | ${PARALELL} python scripts/parse_wikidata_nokana.py > $@

jsonl/custom.jsonl: data/custom.csv data/custom.d
	python scripts/parse_custom_data.py > $@

# Anonymise names
jsonl/researchmap.jsonl jsonl/seijiyama.jsonl: jsonl/%.jsonl: data/%.jsonl
	python scripts/split_names.py < $< | sort > $@

data/researchmap.jsonl:
	${ZCAT} data/researchmap.gz | ${PARALLEL} python scripts/import_researchmap.py > $@

jsonl/jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@

jsonl/myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	python scripts/parse_myoji_yurai.py < $^ > $@

jsonl/koujien.jsonl: data/koujien.json.gz
	${ZCAT} $< | python scripts/parse_koujien.py > $@

jsonl/daijisen.jsonl: data/daijisen.json.gz
	${ZCAT} $< | python scripts/parse_daijisen.py > $@

jsonl/pdd.jsonl: data/pdd.json.gz
	${ZCAT} $< | python scripts/parse_pdd.py > $@
