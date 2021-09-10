"""
Fetch name data from the Wikidata project.
"""
import sys
import json
from functools import reduce
import time
import logging

from SPARQLWrapper import SPARQLWrapper, JSON

from yomikun.models import NameData

endpoint_url = "https://query.wikidata.org/sparql"

base_query = """
SELECT DISTINCT
  ?item ?itemLabel ?itemDescription ?kana ?genderLabel ?dob ?dod ?countryLabel ?nativeName ?ethnicGroupLabel ?birthName ?birthNameKana
WHERE
{
  ?item wdt:P1814 ?kana .  # which have 'name in kana'
  ?item wdt:P31 wd:Q5 .    # find humans
  OPTIONAL {?item wdt:P21 ?gender .}  # also fetch gender
  OPTIONAL {?item wdt:P569 ?dob .}
  OPTIONAL {?item wdt:P570 ?dod .}
  OPTIONAL {?item wdt:P27 ?country .}
  OPTIONAL {?item wdt:P1559 ?nativeName .}
  OPTIONAL {?item wdt:P172 ?ethnicGroup .}
  SERVICE wikibase:label { bd:serviceParam wikibase:language "ja,en". }
  FILTER(STRSTARTS(?kana, '$PREFIX'))
}
"""


def get_results(endpoint_url, query):
    user_agent = "rjh-fetch-japanese-name-data/0.1 (richardjharris@gmail.com)"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


def fetch_wikidata(prefix: str):
    query = base_query.replace('$PREFIX', prefix)
    try:
        result = get_results(endpoint_url, query)
        bindings = result['results']['bindings']
        for binding in bindings:
            print(json.dumps(binding, ensure_ascii=True))
        # Mark prefix as done
        print(prefix, file=sys.stderr)
    except:
        logging.exception(f"Error processing prefix {prefix}")


kanatab = """
あいうえお
かきくけこ
さしすせそ
たちつてと
なにぬねの
はひふへほ
まみむめも
や　ゆ　よ
らりるれろ
わゐ　ゑを
ん
がぎぐげご
ざじずぜぞ
だぢづでど
ばびぶべぼ
ぱぴぷぺぽ
"""

kanas = reduce(list.__add__, (list(s) for s in kanatab.split()))
for kana in kanas:
    fetch_wikidata(prefix=kana)
    time.sleep(5)