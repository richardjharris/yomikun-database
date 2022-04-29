import sys
import json
import click

from yomikun.models import NameData
from yomikun.romajidb import make_romajidb
from yomikun.utils.timer import Timer

@click.command()
def build_romaji_db():
    """
    Build RomajiDB from JSONL data

    RomajiDB is for helping convert ambiguous romaji (such as Goto Yuusuke
    rather than Gotou Yuusuke) into kana using the kanji as a hint.

    We take all the JSON data, except those tagged with xx-romaji (which were
    themselves generated from ambiguous romaji, so we don't accidentally
    create a feedback loop). Then generate a mapping of (kanji, romaji_key, mei/sei) -> (kana)

    In most cases there is a clearly obvious choice, in some cases there may be
    multiple viable choices, in which case we do not create an entry at all.
    """
    timer = Timer()
    names = (NameData.from_dict(json.loads(line)) for line in sys.stdin)

    make_romajidb(names, db_out=sys.stdout)

    timer.report('Generated RomajiDB')