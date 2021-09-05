from __future__ import annotations
import tempfile
from dataclasses import dataclass
from collections import defaultdict
import shutil

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from yomikun.loader.models import Person, Name, Base


class Loader():
    def __init__(self, path):
        self.final_path = path
        self.path = tempfile.NamedTemporaryFile()
        self.engine = create_engine('sqlite:///' + self.path.name, future=True)
        self.session = Session(self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_person(self, person: Person):
        self.session.add(person)

    def add_name(self, name: Name):
        self.session.add(name)

    def commit(self):
        self.session.commit()

        # Copy SQLite file to production path
        shutil.copyfile(self.path.name, self.final_path)
