export PYTHONPATH := ${PYTHONPATH}:.

.DELETE_ON_ERROR:

.PHONY: all clean test

JSONLFILES = koujien.jsonl daijisen.jsonl pdd.jsonl wikipedia_ja.jsonl jmnedict.jsonl myoji-yurai.jsonl

names.sqlite: ${JSONLFILES}
	cat $^ | python scripts/load_data.py $@

clean:
	rm -f ${JSONLFILES}
	rm -f names.sqlite

test:
	pytest

koujien.jsonl: data/koujien.json.gz
	zcat $< | python scripts/parse_koujien.py > $@

daijisen.jsonl: data/daijisen.json.gz
	zcat $< | python scripts/parse_daijisen.py > $@

pdd.jsonl: data/pdd.json.gz
	zcat $< | python scripts/parse_pdd.py > $@

wikipedia_ja.jsonl:
	python scripts/parse_wikipedia_ja.py > $@

jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@

myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	python scripts/parse_myoji_yurai.py < $^ > $@
