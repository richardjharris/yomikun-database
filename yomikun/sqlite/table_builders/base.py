import sqlite3
from abc import ABCMeta


class TableBuilderBase(metaclass=ABCMeta):
    """Base class for SQLite table builders."""

    name: str

    test_queries: list[str] = []

    def create(self, cur: sqlite3.Cursor):
        """
        Invoked before loading any data. Should execute the CREATE TABLE statement
        for this table.
        """
        pass

    def handle_row(self, cur: sqlite3.Cursor, row: dict[str, str]):
        """
        Invoked for each input aggregate data row, as a dict. Should either execute
        insert statements for this table using `cur`, or collect data to be inserted
        in the `on_finished` callback.
        """
        pass

    def finish(self, cur: sqlite3.Cursor):
        """
        Invoked after `on_row` has been called for all input data.
        """
        pass

    @classmethod
    def compare(cls, old: sqlite3.Cursor, new: sqlite3.Cursor) -> str:
        """
        Compare two copies of this table across two cursors, and return
        a short textual summary of the changes.

        By default, prints the old and new row counts.
        """

        def row_count(cur: sqlite3.Cursor) -> int:
            cur.execute(f"SELECT COUNT(*) FROM {cls.name}")
            return cur.fetchone()[0]

        old_count = row_count(old)
        new_count = row_count(new)
        diff = new_count - old_count
        plus = '+' if diff > 0 else ''
        return f"{cls.name:20}: {old_count} -> {new_count} ({plus}{diff})"
