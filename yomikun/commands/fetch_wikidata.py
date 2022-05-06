import json
import logging
import sys
import time
from functools import reduce

import click
from SPARQLWrapper import JSON, SPARQLWrapper

ENDPOINT_URL = "https://query.wikidata.org/sparql"

USER_AGENT = "rjh-fetch-japanese-name-data/0.1 (richardjharris@gmail.com)"

# List of all kana, used to make per-kana queries of the dataset
KANATAB = """
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

BASE_QUERY = """
SELECT DISTINCT
  ?item ?itemLabel ?itemDescription ?kana ?genderLabel ?dob ?dod ?countryLabel ?nativeName
  ?ethnicGroupLabel ?birthName ?birthNameKana
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


@click.command()
def fetch_wikidata():
    """
    Fetch name data from the WikiData project
    """
    kanas = reduce(list.__add__, (list(s) for s in KANATAB.split()))
    for kana in kanas:
        _fetch_wikidata(prefix=kana)
        time.sleep(5)


def get_results(endpoint_url, query) -> dict:
    sparql = SPARQLWrapper(endpoint_url, agent=USER_AGENT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    result = sparql.query().convert()
    assert isinstance(result, dict)
    return result


def _fetch_wikidata(prefix: str):
    query = BASE_QUERY.replace('$PREFIX', prefix)
    try:
        result = get_results(ENDPOINT_URL, query)
        bindings = result['results']['bindings']
        for binding in bindings:
            print(json.dumps(binding, ensure_ascii=True))
        # Mark prefix as done
        print(prefix, file=sys.stderr)
    except Exception:
        logging.exception(f"Error processing prefix {prefix}")
