import os
import traceback
from datetime import datetime
from flask_restful import Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from flask import request, url_for, current_app

from app.models import get_db
from app.models.image import Image
from app.utils.auth_decorator import login_required
from app.services.image_processor import ImageListService, ImageService, ImageTransformService


class ImageListResource(Resource):
    def __init__(self):
        self.db = next(get_db())
        self.image_service = ImageListService(self.db)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('file',
                                 type=FileStorage,  # 文件存储对象
                                 location='files',
                                 help='Image file is required',
                                 )
        super().__init__()

    @login_required
    def post(self, current_user=None):
        args = self.parser.parse_args()
        file = args['file']

        # 验证文件类型
        if not self.image_service.allowed_file(file.filename):
            return {'message': 'File type not allowed'}, 400

        try:
            # 生成安全的文件名
            storage_name = Image.generate_storage_name(file.filename)
            file_path = Image.get_file_path(storage_name)

            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # 检查目录权限
            if not os.access(os.path.dirname(file_path), os.W_OK):
                return {'message': 'Directory is not writable'}, 500

            # 保存文件
            file.save(file_path)

            # 确认文件是否存在
            if not os.path.exists(file_path):
                return {'message': 'File was not saved properly'}, 500

            # 创建数据库记录
            new_image = Image(
                filename=secure_filename(file.filename),
                storage_name=storage_name,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                mime_type=file.content_type,
                user_id=current_user.id
            )

            self.image_service.create_image(new_image)

            # 生成图片访问URL
            image_url = url_for('get_image',
                                image_id=new_image.id,
                                _external=True)

            return {
                'message': 'Image uploaded successfully',
                'image': {
                    'id': new_image.id,
                    'filename': new_image.filename,
                    'url': image_url,
                    'size': new_image.file_size,
                    'mime_type': new_image.mime_type,
                    'created_at': str(new_image.created_at),
                    'user_id': current_user.id
                }
            }, 201

        except Exception as e:
            self.db.rollback()
            if os.path.exists(file_path):
                os.remove(file_path)
            # 打印完整的异常堆栈
            print("Exception occurred:", traceback.format_exc())
            return {'message': f'Upload failed: {str(e)}'}, 500

    def get(self, current_user=None):
        images = self.image_service.get_image_by_user_id(current_user.id)
        return {'images': [image.to_dict() for image in images]}, 200


class ImageResource(Resource):
    def __init__(self):
        self.db = next(get_db())
        self.image_service = ImageService(self.db)
        super().__init__()

    @login_required
    def get(self, image_id: int, current_user=None):
        try:
            image = self.image_service.get_image_by_id(image_id)
            return {'message': 'Image retrieved successfully',
                    'image': {'id': image.id,
                              'filename': image.filename,
                              'url': image.file_path,
                              'size': image.file_size,
                              'mime_type': image.mime_type,
                              'created_at': str(image.created_at),
                              'user_id': image.user_id}
                    }, 200
        except Exception as e:
            return {'message': f'Get image failed: {str(e)}'}, 500

    @login_required
    def delete(self, image_id: int, current_user=None):
        try:
            self.image_service.delete_image(image_id)
            return {'message': 'Image deleted successfully'}, 200
        except Exception as e:
            return {'message': f'Delete failed: {str(e)}'}, 500

    @login_required
    def put(self, image_id: int, current_user=None):
        try:
            self.image_service.update_image(image_id)
            return {'message': 'Image updated successfully'}, 200
        except Exception as e:
            return {'message': f'Update failed: {str(e)}'}, 500


class ImageTransformResource(Resource):
    def __init__(self):
        self.db = next(get_db())
        self.image_tran_service = ImageTransformService(self.db)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('transformations', type=dict,
                                 required=True, help='Transformations type is required')
        super().__init__()

    @login_required
    def post(self, image_id: int, current_user=None):
        args = self.parser.parse_args()
        transformations = args['transformations']

        # 验证转换参数
        if not self.image_tran_service.validate_transformations(transformations):
            return {'message': 'Invalid transformation parameters'}, 400

        return {
            'message' : 'Image Successfully Transformed',
            'image' : self.image_tran_service.process_image(image_id, transformations)
        }, 202
