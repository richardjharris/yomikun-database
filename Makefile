export PYTHONPATH := ${PYTHONPATH}:.
export TMPDIR = ./tmp
export PATH := ${PATH}:.env/bin

SHELL = /bin/bash -o pipefail

mproc ?= 8

ifeq ($(mproc),1)
  PARALLEL=
else
  PARALLEL=parallel --will-cite --gnu -k --pipe -j $(mproc) --tmpdir $(TMPDIR)
endif

ZCAT = scripts/pzcat
CAT = pv
YOMIKUN = yomikun

# Much faster than bzcat
BZCAT = lbzcat

export ROMAJIDB_TSV_PATH = data/romajidb.tsv.gz

.DELETE_ON_ERROR:

.PHONY: all clean test prep prep-perl prep-dev deadcode cover lint pylint install isort

JSONL = koujien daijisen pdd jmnedict myoji-yurai wikipedia_en wikipedia_ja wikidata wikidata-nokana custom researchmap seijiyama
JSONLFILES = $(JSONL:%=jsonl/%.jsonl)

SOURCE_FILES = tests/*.py yomikun scripts/*.py

# Installs to the app assets folder for distribution
install: db/final.db
	cp $< ../app/assets/namesdb.sqlite3
	sqlite3 --csv --noheader $< 'pragma user_version' > ../app/assets/namesdb.version.txt 2>/dev/null

db/final.db: db/final.jsonl
	rm -f $@ && $(YOMIKUN) build-sqlite $@ < $<

db/final.jsonl: db/deduped.jsonl
	$(YOMIKUN) build-final-database < $< > $@

db/gender.jsonl: db/deduped.jsonl data/name_lists.json
	$(YOMIKUN) build-gender-db < $< > $@

clean:
	rm -f ${JSONLFILES}
	rm -f db/deduped.jsonl db/final.jsonl

test:
	pytest

cover:
	rm -rf .coverage htmlcov
	coverage run -m pytest
	coverage html
	(sleep 1 && xdg-open http://localhost:8111) & python -m http.server --directory htmlcov 8111

prep:
	# Wheel is required for jamdict-data
	pip install wheel
	pip install -r requirements.txt
	# Makes 'yomikun' script available without modifying PATH
	pip install --editable .

prep-dev: prep
	pip install -r requirements-dev.txt

prep-perl:
	cpanm MediaWiki::DumpFile::FastPages JSON::XS

deadcode: vulture-whitelist
	vulture vulture-whitelist $(SOURCE_FILES)

vulture-whitelist:
	-vulture --make-whitelist > $@

lint:
	-flake8 $(SOURCE_FILES)

pylint:
	-pylint $(SOURCE_FILES)

isort:
	isort $(SOURCE_FILES)

db/deduped.jsonl: ${JSONLFILES}
	$(YOMIKUN) person-dedupe < $^ > $@

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
	${CAT} jsonl/* | $(YOMIKUN) build-romajidb | gzip -9f > $@

jsonl/wikipedia_en.jsonl: data/enwiki-template-only.gz
	${ZCAT} $< | $(PARALLEL) $(YOMIKUN) parse-wikipedia --lang=en > $@

jsonl/wikipedia_ja.jsonl: data/jawiki-articles.gz
	${ZCAT} data/jawiki-articles.gz | $(PARALLEL) $(YOMIKUN) parse-wikipedia --lang=ja > $@

jsonl/wikidata.jsonl: data/wikidata.jsonl.gz
	${ZCAT} $< | ${PARALLEL} $(YOMIKUN) parse-wikidata > $@ 2>/dev/null

jsonl/wikidata-nokana.jsonl: data/wikidata-nokana.jsonl.gz
	${ZCAT} $< | ${PARALELL} $(YOMIKUN) parse-wikidata-nokana > $@

jsonl/custom.jsonl: data/custom.csv data/custom.d
	$(YOMIKUN) parse-custom-data data/custom.csv data/custom.d/* > $@

# Anonymise names
jsonl/researchmap.jsonl jsonl/seijiyama.jsonl: jsonl/%.jsonl: data/%.jsonl
	$(YOMIKUN) split-names < $< | sort > $@

data/researchmap.jsonl:
	${ZCAT} data/researchmap.gz | ${PARALLEL} $(YOMIKUN) import-researchmap > $@

jsonl/jmnedict.jsonl:
	$(YOMIKUN) parse-jmnedict > $@

jsonl/myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	$(YOMIKUN) parse-myoji-yurai < $^ > $@

jsonl/koujien.jsonl: data/koujien.json.gz
	${ZCAT} $< | $(YOMIKUN) parse-koujien > $@

jsonl/daijisen.jsonl: data/daijisen.json.gz
	${ZCAT} $< | $(YOMIKUN) parse-daijisen > $@

jsonl/pdd.jsonl: data/pdd.json.gz
	${ZCAT} $< | $(YOMIKUN) parse-pdd > $@
