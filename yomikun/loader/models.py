from __future__ import annotations

import enum

import yomikun.models

from sqlalchemy import Column, Integer, String, Boolean, Enum, UniqueConstraint, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Gender(enum.Enum):
    unknown = 1
    male = 2
    female = 3
    neutral = 4


# TODO conflict with NameData.name_type, rename?
class NameType(enum.Enum):
    unknown = 1
    sei = 2
    mei = 3


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    kaki = Column(String)
    yomi = Column(String)
    birth_year = Column(Integer)
    death_year = Column(Integer)


class Name(Base):
    __tablename__ = 'name'
    kaki = Column(String, primary_key=True)
    yomi = Column(String, primary_key=True)
    name_type = Column(Enum(NameType), primary_key=True)
    earliest_year = Column(Integer)
    latest_year = Column(Integer)
    sighting_real = Column(Integer, nullable=False, default=0)
    sighting_pseudo = Column(Integer, nullable=False, default=0)
    sighting_fictional = Column(Integer, nullable=False, default=0)
    is_top5000 = Column(Boolean, nullable=False, default=False)
    gender = Column(Enum(Gender), nullable=False,
                    default=Gender.unknown)

    def __init__(self, **kwargs):
        # Work around SQLAlchemy not using SQLite defaults until row is inserted
        self.sighting_real = 0
        self.sighting_pseudo = 0
        self.sighting_fictional = 0
        self.is_top5000 = False
        self.gender = Gender.unknown
        super().__init__(**kwargs)

    def record_year(self, year: int | None):
        if year is None:
            return
        self.earliest_year = min(
            filter(None.__ne__, [self.earliest_year, year]))
        self.latest_year = max(
            filter(None.__ne__, [self.latest_year, year]))

    def record_sighting(self, typ: yomikun.models.NameType):
        if typ == yomikun.models.NameType.FICTIONAL:
            self.sighting_fictional += 1
        elif typ == yomikun.models.NameType.PSEUDO:
            self.sighting_pseudo += 1
        else:
            self.sighting_real += 1

    def record_gender(self, gender: Gender):
        """
        Update the gender information for this name.
        Fun four-value logic here!
        """
        if self.gender == Gender.unknown:
            self.gender = gender
        elif self.gender == Gender.neutral:
            pass
        elif (self.gender == Gender.male and gender == Gender.female) or \
                (self.gender == Gender.female and gender == Gender.male):
            self.gender = Gender.neutral
        else:
            # no-op
            pass

    def set_top5000(self):
        self.is_top5000 = True
