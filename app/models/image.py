import os
from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from . import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255))
    storage_name = Column(String(255))
    file_path = Column(String(255))
    file_size = Column(Integer)
    mime_type = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.now)  # 使用datetime.utcnow
    updated_at = Column(DateTime, default=datetime.now,
                        onupdate=datetime.now)  # 同样使用datetime.utcnow

    # 建立与用户的关系 -- 双向关系
    user = relationship("User", back_populates="images")

    @staticmethod
    def generate_storage_name(filename):
        ext = os.path.splitext(filename)[1]
        return f"{uuid4()}{ext}"

    @staticmethod
    def get_file_path(storage_name):
        today = datetime.now()
        return os.path.join('uploads', str(today.year), str(today.month), storage_name)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'storage_name': self.storage_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            # 将datetime对象转换为UNIX时间戳的方法
            'created_at': datetime.timestamp(self.created_at) if self.created_at else None,
            'updated_at': datetime.timestamp(self.updated_at) if self.updated_at else None
        }
