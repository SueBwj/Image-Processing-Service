from functools import wraps
from flask import request
from .jwt_utils import decode_jwt_token
from app.models import get_db
from app.models.user import User


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # 从请求头获取token
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            return {'message': 'Token is missing'}, 401

        try:
            # 解码token
            payload = decode_jwt_token(token)
            print(payload)

            # 获取用户
            db = next(get_db())
            current_user = db.query(User).filter(
                User.id == payload['user_id']
            ).first()

            if not current_user:
                return {'message': 'Invalid token'}, 401

            # 将用户信息添加到kwargs
            kwargs['current_user'] = current_user

        except Exception as e:
            return {'message': 'Invalid token'}, 401

        return f(*args, **kwargs)
    return decorated
