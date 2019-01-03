from functools import wraps
from flask import request
from utils.Response import Response
from utils.Security import SecurityUtils
from utils.ErrorUtils import ErrorMsg

class MiddlewareUtils:
    @staticmethod
    def valid_user(f):
        @wraps(f)
        def logged_in_route(*args, **kwargs):
            user_id = request.headers.get('Authorization')
            room_number = kwargs['room_number']
            is_allowed = SecurityUtils.checkUser(room_number, user_id)
            if is_allowed:
                return f(*args, **kwargs)
            else:
                return Response.responseFailure(ErrorMsg.NO_USER.value)

        return logged_in_route

    @staticmethod
    def valid_master(f):
        @wraps(f)
        def master_in_route(*args, **kwargs):
            user_id = request.headers.get('Authorization')
            room_number = kwargs['room_number']
            is_allowed = SecurityUtils.checkUser(room_number, user_id, True)
            if is_allowed:
                return f(*args, **kwargs)
            else:
                return Response.responseFailure(ErrorMsg.NO_MASTER.value)

        return master_in_route