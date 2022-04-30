# Mapping of namedata part names to their IDs. This is done as SQLite
# does not support enums.
from typing import Any, Iterable


PART_ID = {
    "unknown": 0,
    "sei": 1,
    "mei": 2,
}

SqliteQuery = tuple[str, Iterable[Any]]
