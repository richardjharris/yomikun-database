export PYTHONPATH := ${PYTHONPATH}:.

.DELETE_ON_ERROR:

.PHONY: jsonl

JSONLFILES = koujien.jsonl daijisen.jsonl pdd.jsonl wikipedia.jsonl jmnedict.jsonl myoji-yurai.jsonl

jsonl: ${JSONLFILES}

clean:
	rm ${JSONLFILES}

koujien.jsonl: data/koujien.json.gz
	zcat $^ | python scripts/parse_koujien.py > $@

daijisen.jsonl: data/daijisen.json.gz
	zcat $^ | python scripts/parse_daijisen.py > $@

pdd.jsonl: data/pdd.json.gz
	zcat $^ | python scripts/parse_pdd.py > $@

wikipedia.jsonl:
	python scripts/parse_wikipedia.py > $@

jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@

myoji-yurai.jsonl: data/myoji-yurai-readings.csv
	python scripts/parse_myoji_yurai.py < $^ > $@