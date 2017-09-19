# -*- coding: utf-8 -*-
import datetime
import json
from copy import deepcopy
from marshmallow import Schema, fields, post_load
from marshmallow.validate import OneOf
from festival.models import *


def partial_schema_factory(schema_cls):
    schema = schema_cls(partial=True)
    for field_name, field in schema.fields.items():
        if isinstance(field, fields.Nested):
            new_field = deepcopy(field)
            new_field.schema.partial = True
            schema.fields[field_name] = new_field
    return schema


def load_json(str_value):
    try:
        return json.loads(str_value)
    except:
        return "Error loading JSON"


# region Protected\s*
# endregion


class CityCreateRequestSchema(Schema):
    """ JSON serialization schema """
    name = fields.String(required=True)
    slug = fields.String(required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of City"""
        return City(**data)

    class Meta:
        ordered = True


class CityListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    slug = fields.String(required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of City"""
        return City(**data)

    class Meta:
        ordered = True


class CityItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    slug = fields.String(required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of City"""
        return City(**data)

    class Meta:
        ordered = True


class ExperimentCreateRequestSchema(Schema):
    """ JSON serialization schema """
    date = fields.DateTime(required=True)
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    city = fields.Nested(
        'festival.schema.CityCreateRequestSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Experiment"""
        return Experiment(**data)

    class Meta:
        ordered = True


class ExperimentListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    date = fields.DateTime(required=True)
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    city = fields.Nested(
        'festival.schema.CityListResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Experiment"""
        return Experiment(**data)

    class Meta:
        ordered = True


class ExperimentItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    date = fields.DateTime(required=True)
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    city = fields.Nested(
        'festival.schema.CityItemResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Experiment"""
        return Experiment(**data)

    class Meta:
        ordered = True


class GridCellCreateRequestSchema(Schema):
    """ JSON serialization schema """
    north_latitude = fields.Decimal(required=True)
    south_latitude = fields.Decimal(required=True)
    east_longitude = fields.Decimal(required=True)
    west_longitude = fields.Decimal(required=True)
    city = fields.Nested(
        'festival.schema.CityCreateRequestSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of GridCell"""
        return GridCell(**data)

    class Meta:
        ordered = True


class GridCellListResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    north_latitude = fields.Decimal(required=True)
    south_latitude = fields.Decimal(required=True)
    east_longitude = fields.Decimal(required=True)
    west_longitude = fields.Decimal(required=True)
    city = fields.Nested(
        'festival.schema.CityListResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of GridCell"""
        return GridCell(**data)

    class Meta:
        ordered = True


class GridCellItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    north_latitude = fields.Decimal(required=True)
    south_latitude = fields.Decimal(required=True)
    east_longitude = fields.Decimal(required=True)
    west_longitude = fields.Decimal(required=True)
    city = fields.Nested(
        'festival.schema.CityItemResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of GridCell"""
        return GridCell(**data)

    class Meta:
        ordered = True


class ResultCreateRequestSchema(Schema):
    """ JSON serialization schema """
    date = fields.DateTime(required=True)
    updated = fields.DateTime(required=True)
    value = fields.Float(required=False, allow_none=True)
    grid_cell = fields.Nested(
        'festival.schema.GridCellCreateRequestSchema',
        required=True)
    experiment = fields.Nested(
        'festival.schema.ExperimentCreateRequestSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Result"""
        return Result(**data)

    class Meta:
        ordered = True


class ResultListResponseSchema(Schema):
    """ JSON serialization schema """
    value = fields.Float(required=False, allow_none=True)
    latitude = fields.Function(lambda x: float(
        x.grid_cell.north_latitude + x.grid_cell.south_latitude) * .5)
    longitude = fields.Function(lambda x: float(
        x.grid_cell.east_longitude + x.grid_cell.west_longitude) * .5)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Result"""
        return Result(**data)

    class Meta:
        ordered = True


class ResultItemResponseSchema(Schema):
    """ JSON serialization schema """
    value = fields.Float(required=False, allow_none=True)
    latitude = fields.Function(lambda x: float(
        x.grid_cell.north_latitude + x.grid_cell.south_latitude) * .5)
    longitude = fields.Function(lambda x: float(
        x.grid_cell.east_longitude + x.grid_cell.west_longitude) * .5)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Result"""
        return Result(**data)

    class Meta:
        ordered = True

