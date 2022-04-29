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