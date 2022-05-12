import sqlite3
from abc import ABCMeta


class TableBase(metaclass=ABCMeta):
    """Base class for SQLite tables."""

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
