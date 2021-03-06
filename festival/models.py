# -*- coding: utf-8 -*-
import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, \
    Enum, DateTime, Numeric, Text, Unicode, UnicodeText
from sqlalchemy import event
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy_i18n import make_translatable, translation_base, Translatable

make_translatable(options={'locales': ['pt', 'en', 'es'],
                           'auto_create_locales': True,
                           'fallback_locale': 'en'})

db = SQLAlchemy()


# noinspection PyClassHasNoInit
class ResultType:
    TOPIC = 'TOPIC'
    TRAFFIC_JAM = 'TRAFFIC_JAM'
    SENTIMENT = 'SENTIMENT'

    @staticmethod
    def values():
        return [n for n in ResultType.__dict__.keys()
                if n[0] != '_' and n != 'values']


class City(db.Model):
    """ City """
    __tablename__ = 'city'

    # Fields
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(50), nullable=False)

    def __unicode__(self):
        return self.name

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class Experiment(db.Model):
    """ Experiment """
    __tablename__ = 'experiment'

    # Fields
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    type = Column(Enum(*ResultType.values(),
                       name='ResultTypeEnumType'), nullable=False)

    # Associations
    city_id = Column(Integer,
                     ForeignKey("city.id"), nullable=False)
    city = relationship(
        "City",
        foreign_keys=[city_id])

    def __unicode__(self):
        return self.date

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class GridCell(db.Model):
    """ A grid cell for displaying results for EUBra-BIGSEA """
    __tablename__ = 'grid_cell'

    # Fields
    id = Column(Integer, primary_key=True)
    north_latitude = Column(Numeric(12, 8), nullable=False)
    south_latitude = Column(Numeric(12, 8), nullable=False)
    east_longitude = Column(Numeric(12, 8), nullable=False)
    west_longitude = Column(Numeric(12, 8), nullable=False)

    # Associations
    city_id = Column(Integer,
                     ForeignKey("city.id"), nullable=False)
    city = relationship(
        "City",
        foreign_keys=[city_id])

    def __unicode__(self):
        return self.north_latitude

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)


class Result(db.Model):
    """ Result """
    __tablename__ = 'result'

    # Fields
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    updated = Column(DateTime, nullable=False)
    value = Column(Float)

    # Associations
    grid_cell_id = Column(Integer,
                          ForeignKey("grid_cell.id"), nullable=False)
    grid_cell = relationship(
        "GridCell",
        foreign_keys=[grid_cell_id])
    experiment_id = Column(Integer,
                           ForeignKey("experiment.id"), nullable=False)
    experiment = relationship(
        "Experiment",
        foreign_keys=[experiment_id])

    def __unicode__(self):
        return self.date

    def __repr__(self):
        return '<Instance {}: {}>'.format(self.__class__, self.id)

