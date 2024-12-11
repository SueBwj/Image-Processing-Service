from flask import Flask
from flask_restful import Api
from app.resources import init_resources
from app.models import create_tables

app = Flask(__name__)
api = Api(app)
init_resources(api)


if __name__ == '__main__':
    create_tables()  # 创建数据库表
    app.run(debug=True)
