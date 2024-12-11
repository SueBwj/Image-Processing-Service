from datetime import datetime
import pdb
from flask import jsonify
from flask_restful import Resource, reqparse
from werkzeug.security import generate_password_hash
from app.models import get_db
from app.models.user import User
from sqlalchemy.exc import IntegrityError
from app.utils.jwt_utils import generate_jwt_token
from werkzeug.security import check_password_hash


class RegisterResource(Resource):
    def __init__(self) -> None:
        # 处理post和put请求时，解析请求体中的参数，所以要使用parser； 处理url查询字符的时候，/user/<int:user_id> 或者使用get的时候使用函数参数
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str,
                                 required=True, help='user name is required')
        self.parser.add_argument('password', type=str,
                                 required=True, help='password is required')
        super().__init__()

    def post(self):
        args = self.parser.parse_args()
        db = next(get_db())

        try:
            # 检查用户名是否存在
            existing_user = db.query(User).filter(
                User.username == args['username']
            ).first()

            if existing_user:
                return {'message': 'Username already exists'}, 400

            new_user = User(username=args['username'],
                            password=generate_password_hash(args['password']), created_at=datetime.now(), updated_at=datetime.now())

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # jwt-token -- 如果注册后直接登录，则需要生成jwt-token
            # token = generate_jwt_token(new_user.id)
            return {
                'message': 'User registered successfully',
                'user': new_user.to_dict(),
                # 'token': token
            }, 201
        except Exception as e:
            db.rollback()
            return {'message': str(e)}, 500


class LoginResource(Resource):
    def __init__(self) -> None:
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('username', type=str,
                                 required=True, help='user name is required')
        self.parser.add_argument('password', type=str,
                                 required=True, help='password is required')
        super().__init__()

    def post(self):
        args = self.parser.parse_args()
        db = next(get_db())

        try:
            user = db.query(User).filter(
                User.username == args['username']
            ).first()

            if not user or not check_password_hash(user.password, args['password']):
                return {'message': 'Invalid username or password'}, 401

            token = generate_jwt_token(user.id)

            return {
                'message': 'Login successful',
                'user': user.to_dict(),
                'token': token
            }, 200

        except Exception as e:
            return {'message': str(e)}, 500
