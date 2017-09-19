# -*- coding: utf-8 -*-}
import json
import logging
from collections import namedtuple
from functools import wraps

from flask import request, Response, g, current_app

logger = logging.getLogger(__name__)
User = namedtuple("User", "id, login, email, first_name, last_name, locale")

MSG1 = 'Could not verify your access level for that URL. ' \
       'You have to login with proper credentials provided by Lemonade Thorn'

MSG2 = 'Could not verify your access level for that URL. ' \
       'Invalid authentication token'

CONFIG_KEY = 'FESTIVAL_CONFIG'


def authenticate(msg, extra_info):
    """Sends a 401 response that enables basic auth"""
    logging.info('User parameters: %s', json.dumps(extra_info))
    return Response(json.dumps({'status': 'ERROR', 'message': msg}), 401,
                    mimetype="application/json")


def requires_auth(f):
    @wraps(f)
    def decorated(*_args, **kwargs):
        config = current_app.config[CONFIG_KEY]
        internal_token = request.args.get('token',
                                          request.headers.get('x-auth-token'))

        if internal_token:
            if internal_token == str(config['secret']):
                setattr(g, 'user',
                        User(0, '', '', '', '', ''))  # System user
                return f(*_args, **kwargs)
            else:
                return authenticate(MSG2, {})
        else:
            return authenticate(MSG1, {})

    return decorated
