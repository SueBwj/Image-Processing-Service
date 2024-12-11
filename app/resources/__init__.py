from flask_restful import Api


def init_resources(api: Api):
    from .auth import RegisterResource, LoginResource
    from .image import ImageResource, ImageListResource, ImageTransformResource

    # 注册认证相关路由
    api.add_resource(RegisterResource, '/register')
    api.add_resource(LoginResource, '/login')

    # 注册图片相关路由
    api.add_resource(ImageResource, '/image/<int:image_id>',
                     endpoint='get_image')
    api.add_resource(ImageListResource, '/images')
    api.add_resource(ImageTransformResource,
                     '/images/<int:image_id>/transform')
