import datetime
from dotenv import load_dotenv
import jwt
import os
from typing import Dict

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)


def generate_jwt_token(user_id: int) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.timestamp(datetime.datetime.now() + JWT_EXPIRATION_DELTA),
        'iat': datetime.datetime.timestamp(datetime.datetime.now())
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def decode_jwt_token(token: str) -> Dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=JWT_ALGORITHM)
