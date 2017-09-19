# -*- coding: utf-8 -*-}
from app_auth import requires_auth
from flask import request, current_app
from flask_restful import Resource
from schema import *
from sqlalchemy.orm import joinedload


def is_digit(v):
    if v[0] == '-':
        return v[1:].replace('.', '', 1).isdigit()
    else:
        return v.replace('.', '', 1).isdigit()


class ResultListApi(Resource):
    """ REST API for listing class Result """

    @staticmethod
    @requires_auth
    def get():
        results, result_code = {}, 200
        if request.args.get('fields'):
            only = [f.strip() for f in
                    request.args.get('fields').split(',')]
        else:
            only = ('id', 'name') if request.args.get(
                'simple', 'false') == 'true' else None
        latitude = request.args.get('latitude')
        longitude = request.args.get('longitude')
        result_type = request.args.get('type')
        min_value = float(request.args.get('min', '0'))

        # ts = request.args.get('ts', )
        if not result_type or result_type not in ResultType.values():
            results = {'status': 'ERROR', 'message': 'Invalid result type'}
            result_code = 400
        elif latitude and longitude:
            # results = {
            #     'status': 'ERROR',
            #     'message': ('At least one parameter is missing (latitude, '
            #                 'longitude or type ')}
            if not (is_digit(longitude) and is_digit(latitude)):
                results = {
                    'status': 'ERROR',
                    'message': 'Latitude and longitude must be numbers'}
                result_code = 400
            else:
                results = {'data': ResultListResponseSchema(
                    many=True, only=only).dump(
                    db.session.query(Result) \
                        .join(Experiment)
                        .options(joinedload(Result.grid_cell)).filter(
                        Experiment.type == result_type,
                        GridCell.north_latitude >= float(latitude),
                        GridCell.south_latitude <= float(latitude),
                        GridCell.east_longitude >= float(longitude),
                        GridCell.west_longitude <= float(longitude),
                        Result.value >= min_value
                    )).data}
        else:
            results = {'data': ResultListResponseSchema(
                many=True, only=only).dump(
                Result.query.join(Experiment) \
                    .options(joinedload(Result.grid_cell)).filter(
                    Experiment.type == result_type,
                    Result.value >= min_value
                )).data}

        db.session.rollback()
        return results, result_code

    @staticmethod
    @requires_auth
    def post():
        result, result_code = dict(
            status="ERROR", message="Missing json in the request body"), 400
        if request.json is not None:
            request_schema = ResultCreateRequestSchema()
            response_schema = ResultItemResponseSchema()
            form = request_schema.load(request.json)
            if form.errors:
                result, result_code = dict(
                    status="ERROR", message="Validation error",
                    errors=form.errors), 400
            else:
                try:
                    result = form.data
                    db.session.add(result)
                    db.session.commit()
                    result, result_code = response_schema.dump(
                        result).data, 200
                except Exception, e:
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()

        return result, result_code


class ResultDetailApi(Resource):
    """ REST API for a single instance of class Result """

    @staticmethod
    @requires_auth
    def get(result_id):
        result = Result.query.get(result_id)
        if result is not None:
            return ResultItemResponseSchema().dump(result).data
        else:
            return dict(status="ERROR", message="Not found"), 404

    @staticmethod
    @requires_auth
    def delete(result_id):
        result, result_code = dict(status="ERROR", message="Not found"), 404

        result = Result.query.get(result_id)
        if result is not None:
            try:
                db.session.delete(result)
                db.session.commit()
                result, result_code = dict(status="OK", message="Deleted"), 200
            except Exception, e:
                result, result_code = dict(status="ERROR",
                                           message="Internal error"), 500
                if current_app.debug:
                    result['debug_detail'] = e.message
                db.session.rollback()
        return result, result_code

    @staticmethod
    @requires_auth
    def patch(result_id):
        result = dict(status="ERROR", message="Insufficient data")
        result_code = 404

        if request.json:
            request_schema = partial_schema_factory(ResultCreateRequestSchema)
            # Ignore missing fields to allow partial updates
            form = request_schema.load(request.json, partial=True)
            response_schema = ResultItemResponseSchema()
            if not form.errors:
                try:
                    form.data.id = result_id
                    result = db.session.merge(form.data)
                    db.session.commit()

                    if result is not None:
                        result, result_code = dict(
                            status="OK", message="Updated",
                            data=response_schema.dump(result).data), 200
                    else:
                        result = dict(status="ERROR", message="Not found")
                except Exception, e:
                    result, result_code = dict(status="ERROR",
                                               message="Internal error"), 500
                    if current_app.debug:
                        result['debug_detail'] = e.message
                    db.session.rollback()
            else:
                result = dict(status="ERROR", message="Invalid data",
                              errors=form.errors)
        return result, result_code
