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


class GridCellCreateRequestSchema(Schema):
    """ JSON serialization schema """
    north_latitude = fields.Decimal(required=True)
    south_latitude = fields.Decimal(required=True)
    east_longitude = fields.Decimal(required=True)
    west_longitude = fields.Decimal(required=True)

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

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of GridCell"""
        return GridCell(**data)

    class Meta:
        ordered = True


class ResultCreateRequestSchema(Schema):
    """ JSON serialization schema """
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    date = fields.DateTime(required=True)
    updated = fields.DateTime(required=True)
    value = fields.String(required=False, allow_none=True)
    grid_cell = fields.Nested(
        'GridCellCreateRequestSchema',
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
    id = fields.Integer(required=True)
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    date = fields.DateTime(required=True)
    updated = fields.DateTime(required=True)
    value = fields.String(required=False, allow_none=True)
    grid_cell = fields.Nested(
        'GridCellListResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Result"""
        return Result(**data)

    class Meta:
        ordered = True


class ResultItemResponseSchema(Schema):
    """ JSON serialization schema """
    id = fields.Integer(required=True)
    type = fields.String(required=True,
                         validate=[OneOf(ResultType.__dict__.keys())])
    date = fields.DateTime(required=True)
    updated = fields.DateTime(required=True)
    value = fields.String(required=False, allow_none=True)
    grid_cell = fields.Nested(
        'GridCellItemResponseSchema',
        required=True)

    # noinspection PyUnresolvedReferences
    @post_load
    def make_object(self, data):
        """ Deserialize data into an instance of Result"""
        return Result(**data)

    class Meta:
        ordered = True

