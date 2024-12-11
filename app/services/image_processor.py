import os
from PIL import Image as PILImage

from app.models.image import Image
from app.services.cache import RedisCache

class ImageListService:
    def __init__(self, db):
        self.db = db

    def create_image(self, image: Image):
        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)
        return image

    def get_image_by_user_id(self, user_id: int):
        return self.db.query(Image).filter(Image.user_id == user_id).all()

    def allowed_file(self, filename):
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ImageService:
    def __init__(self, db):
        self.db = db

    def get_image_by_id(self, image_id: int):
        return self.db.query(Image).filter(Image.id == image_id).first()

    def update_image(self, image_id: int, new_image: Image):
        db_image = self.get_image_by_id(image_id)
        if db_image:
            db_image.filename = new_image.filename
            db_image.storage_name = new_image.storage_name
            db_image.file_path = new_image.file_path
            db_image.file_size = new_image.file_size
            db_image.mime_type = new_image.mime_type
            self.db.commit()
            return db_image.to_dict()
        return None

    def delete_image(self, image_id: int):
        image = self.get_image_by_id(image_id)
        if image:
            self.db.delete(image)
            self.db.commit()
            # 还需要删除文件夹中的图片
            os.remove(image.file_path)
            return True
        return False


class ImageTransformService:
    def __init__(self, db):
        self.db = db
        self.image_service = ImageService(self.db)
        self.cache = RedisCache()

    def process_image(self, image_id: int, transformations: dict):
        # 缓存
        cache_key = f"image_transform_{image_id}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result
        
        for transformation, params in transformations.items():
            if transformation == 'resize':
                result = self.resize_image(image_id, params)
            elif transformation == 'crop':
                result = self.crop_image(image_id, params)
            elif transformation == 'rotate':
                result = self.rotate_image(image_id, params)
            elif transformation == 'flip':
                result = self.flip_image(image_id, params)

        self.cache.set(cache_key, result, expire=60 * 60 * 24)
        return result

    def resize_image(self, image_id: int, params: dict):
        try:
            # 获取原始图片信息
            image_record = self.image_service.get_image_by_id(image_id)
            if not image_record:
                raise ValueError("Image not found")

            with PILImage.open(image_record.file_path) as img:
                resized_img = img.resize(
                    (params['width'], params['height']),
                    PILImage.Resampling.LANCZOS
                )

                new_filename = f"resized_{image_record.storage_name}"
                new_path = os.path.join(os.path.dirname(
                    image_record.file_path), new_filename)
                resized_img.save(new_path, quality=95)

                return self.image_service.update_image(
                    image_id,
                    Image(
                        filename=f"rotate_{image_record.filename}",
                        storage_name=new_filename,
                        file_path=new_path,
                        file_size=os.path.getsize(new_path),
                        mime_type=image_record.mime_type
                    )
                )
        except Exception as e:
            raise Exception(f"Resize failed: {str(e)}")

    def crop_image(self, image_id: int, params: dict):
        try:
            image_record = self.image_service.get_image_by_id(image_id)
            if not image_record:
                raise ValueError("Image not found")

            with PILImage.open(image_record.file_path) as img:
                cropped_img = img.crop(
                    (params['x'], params['y'], params['x'] + params['width'], params['y'] + params['height']))
                new_filename = f"cropped_{image_record.storage_name}"
                new_path = os.path.join(os.path.dirname(
                    image_record.file_path), new_filename)
                cropped_img.save(new_path, quality=95)

                return self.image_service.update_image(
                    image_id,
                    Image(
                        filename=f"cropped_{image_record.filename}",
                        storage_name=new_filename,
                        file_path=new_path,
                        file_size=os.path.getsize(new_path),
                        mime_type=image_record.mime_type
                    )
                )
        except Exception as e:
            raise Exception(f"Crop failed: {str(e)}")

    def rotate_image(self, image_id: int, params: dict):
        try:
            image_record = self.image_service.get_image_by_id(image_id)
            if not image_record:
                raise ValueError("Image not found")

            with PILImage.open(image_record.file_path) as img:
                # 根据方向翻转图片
                if params.get('direction') == 'horizontal':
                    flipped_img = img.transpose(
                        PILImage.Transpose.FLIP_LEFT_RIGHT)
                else:  # vertical
                    flipped_img = img.transpose(
                        PILImage.Transpose.FLIP_TOP_BOTTOM)

                # 保存处理后的图片
                new_filename = f"rotate_{image_record.storage_name}"
                new_path = os.path.join(os.path.dirname(
                    image_record.file_path), new_filename)
                flipped_img.save(new_path, quality=95)
                new_image = Image(
                    filename=f"rotate_{image_record.filename}",
                    storage_name=new_filename,
                    file_path=new_path,
                    file_size=os.path.getsize(new_path),
                    mime_type=image_record.mime_type
                )
                return self.image_service.update_image(
                    image_id,
                    new_image
                )
        except Exception as e:
            raise Exception(f"Rotate failed: {str(e)}")

    def flip_image(self, image_id: int, params: dict):
        try:
            image_record = self.image_service.get_image_by_id(image_id)
            if not image_record:
                raise ValueError("Image not found")

            with PILImage.open(image_record.file_path) as img:
                # 根据方向翻转图片
                if params.get('direction') == 'horizontal':
                    flipped_img = img.transpose(
                        PILImage.Transpose.FLIP_LEFT_RIGHT)
                else:  # vertical
                    flipped_img = img.transpose(
                        PILImage.Transpose.FLIP_TOP_BOTTOM)

                # 保存处理后的图片
                new_filename = f"flipped_{image_record.storage_name}"
                new_path = os.path.join(os.path.dirname(
                    image_record.file_path), new_filename)
                flipped_img.save(new_path, quality=95)

                return self.image_service.update_image(
                    image_id,
                    Image(
                        filename=f"flipped_{image_record.filename}",
                        storage_name=new_filename,
                        file_path=new_path,
                        file_size=os.path.getsize(new_path),
                        mime_type=image_record.mime_type
                    )
                )
        except Exception as e:
            raise Exception(f"Flip failed: {str(e)}")

    def validate_transformations(self, transformations):
        """验证转换参数的格式和值"""
        allowed_transforms = {'resize', 'crop', 'rotate', 'format', 'filters'}
        if not all(k in allowed_transforms for k in transformations.keys()):
            return False

        # 验证 resize 参数
        if 'resize' in transformations:
            resize = transformations['resize']
            if not isinstance(resize, dict) or \
               not all(k in resize for k in ['width', 'height']) or \
               not all(isinstance(v, (int, float)) for v in resize.values()):
                return False

        # 验证 crop 参数
        if 'crop' in transformations:
            crop = transformations['crop']
            if not isinstance(crop, dict) or \
               not all(k in crop for k in ['width', 'height', 'x', 'y']) or \
               not all(isinstance(v, (int, float)) for v in crop.values()):
                return False

        # 验证 rotate 参数
        if 'rotate' in transformations:
            return True

        # 验证 format 参数
        if 'format' in transformations:
            if not isinstance(transformations['format'], str) or \
               transformations['format'].lower() not in ['jpeg', 'png', 'gif', 'webp']:
                return False

        # 验证 filters 参数
        if 'filters' in transformations:
            filters = transformations['filters']
            if not isinstance(filters, dict) or \
               not all(k in ['grayscale', 'sepia'] for k in filters.keys()) or \
               not all(isinstance(v, bool) for v in filters.values()):
                return False

        return True
