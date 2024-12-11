# 🖼️ Image Processing Service | 图像处理服务

A RESTful image processing service built with Flask, providing image transformation and storage capabilities.

A roadmap pratice project -- https://roadmap.sh/projects/image-processing-service

基于Flask构建的RESTful图像处理服务，提供图像转换和存储功能。

## ✨ Features | 功能特点

- 🔐 User authentication with JWT | 基于JWT的用户认证
- 📤 Image upload and storage | 图片上传与存储
- 🛠️ Image transformations | 图片转换功能
  - Resize | 调整大小
  - Crop | 裁剪
  - Rotate | 旋转
  - Flip | 翻转
- 💾 Redis caching | Redis缓存
- 🗄️ MySQL database | MySQL数据库存储

## 🔧 Tech Stack | 技术栈

- Flask
- SQLAlchemy
- Redis
- JWT
- Pillow
- MySQL

## 🚀 Quick Start | 快速开始

### Prerequisites | 环境要求

```bash
Python 3.8+
Redis
MySQL
```

### Installation | 安装

1. Clone the repository | 克隆仓库
```bash
git clone https://github.com/yourusername/image-processing-service.git
cd image-processing-service
```

2. Install dependencies | 安装依赖
```bash
pip install -r requirements.txt
```

3. Configure environment variables | 配置环境变量
```bash
# Create .env file | 创建.env文件
cp .env.example .env
# Edit .env with your configurations | 编辑配置
```

4. Run the application | 运行应用
```bash
python run.py
```

## 📚 API Documentation | API文档

### Authentication | 认证接口

- `POST /register` - Register new user | 注册新用户
- `POST /login` - User login | 用户登录

### Image Operations | 图片操作

- `POST /images` - Upload image | 上传图片
- `GET /images` - List all images | 获取图片列表
- `GET /image/<id>` - Get specific image | 获取特定图片
- `POST /images/<id>/transform` - Transform image | 转换图片

## 🏗️ Project Structure | 项目结构

```
image_processing_service/
├── app/
│   ├── models/         # Database models | 数据库模型
│   ├── resources/      # API endpoints | API端点
│   ├── services/       # Business logic | 业务逻辑
│   └── utils/          # Utilities | 工具函数
├── config.py           # Configuration | 配置文件
└── run.py             # Application entry | 应用入口
```
