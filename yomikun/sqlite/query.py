import sqlite3

import regex
import romkan

from yomikun.sqlite.models import NamePart


def get_data(
    conn: sqlite3.Connection, search_term: str, part: str, limit: int
) -> sqlite3.Cursor:
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row  # type: ignore

    is_kaki = regex.search(r'\p{Han}', search_term)
    if is_kaki:
        query_col = 'kaki'
    else:
        query_col = 'yomi'
        search_term = romkan.to_roma(search_term)

    if part == 'all':
        part_query = ""
    else:
        part_id = NamePart[part].value
        part_query = f"AND part = {int(part_id)}"

    limit_sql = '' if limit == -1 else f'LIMIT {int(limit)}'

    sql = f"""
        SELECT * FROM names
        WHERE {query_col} = ? {part_query}
        ORDER BY part, hits_total DESC
        {limit_sql}
    """
    cur.execute(sql, (search_term,))
    return cur


def get_exact_match(
    conn: sqlite3.Connection, kaki: str, yomi: str, part: NamePart
) -> sqlite3.Row | None:
    cur = conn.cursor()
    cur.row_factory = sqlite3.Row  # type: ignore

    yomi = romkan.to_roma(yomi)
    part = part.value

    sql = """
        SELECT * FROM names
        WHERE kaki = ? AND yomi = ? AND part = ?
    """
    cur.execute(sql, (kaki, yomi, part))
    return cur.fetchone()
