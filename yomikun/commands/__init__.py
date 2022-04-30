from .build_final_database import build_final_database
from .build_gender_db import build_gender_db
from .build_romaji_db import build_romaji_db
from .build_sqlite import build_sqlite
from .help import make_help_command
from .person_dedupe import person_dedupe
from .parse_jmnedict import parse_jmnedict
from .parse_pdd import parse_pdd
from .parse_daijisen import parse_daijisen
from .parse_koujien import parse_koujien
from .clean_custom_data import clean_custom_data
from .split_names import split_names
from .parse_custom_data import parse_custom_data
from .parse_wikidata import parse_wikidata
from .parse_myoji_yurai import parse_myoji_yurai
from .fetch_wikidata import fetch_wikidata
from .import_researchmap import import_researchmap
from .parse_wikidata_nokana import parse_wikidata_nokana
from .parse_wikipedia_en import parse_wikipedia_en
from .parse_wikipedia_ja import parse_wikipedia_ja
from .gender_model import gender_model

def add_yomikun_commands(cli) -> None:
    """
    Add all known Yomikun commands to the Click cli object.
    """
    cli.add_command(build_final_database)
    cli.add_command(build_gender_db)
    cli.add_command(build_romaji_db)
    cli.add_command(build_sqlite)
    cli.add_command(make_help_command(cli))
    cli.add_command(person_dedupe)
    cli.add_command(parse_jmnedict)
    cli.add_command(parse_pdd)
    cli.add_command(parse_daijisen)
    cli.add_command(parse_koujien)
    cli.add_command(clean_custom_data)
    cli.add_command(split_names)
    cli.add_command(parse_custom_data)
    cli.add_command(parse_wikidata)
    cli.add_command(parse_wikidata_nokana)
    cli.add_command(parse_myoji_yurai)
    cli.add_command(fetch_wikidata)
    cli.add_command(import_researchmap)
    cli.add_command(parse_wikipedia_en)
    cli.add_command(parse_wikipedia_ja)
    cli.add_command(gender_model)