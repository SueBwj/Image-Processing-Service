import redis
import json

# 将健值对存入到cache中，并设置过期时间；
class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)

    def set(self, key, value, expire=None):
        try:
            value_str = json.dumps(value)
            self.redis_client.set(key, value_str, expire)
        except Exception as e:
            print(e)

    def get(self, key):
        try:
            value_str = self.redis_client.get(key)
            return json.loads(value_str)
        except Exception as e:
            print(e)

    def delete(self, key):
        try:
            self.redis_client.delete(key)
        except Exception as e:
            print(e)

