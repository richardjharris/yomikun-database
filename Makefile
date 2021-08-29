PYTHONPATH := "${PYTHONPATH}:/home/rjh/yomikun/database"

koujien.jsonl:
	zcat data/koujien.json.gz | python scripts/parse_koujien.py > $@

daijisen.jsonl:
	zcat data/daijisen.json.gz | python scripts/parse_daijisen.py > $@

wikipedia.jsonl:
	python scripts/parse_wikipedia.py > $@

jmnedict.jsonl:
	python scripts/parse_jmnedict.py > $@
