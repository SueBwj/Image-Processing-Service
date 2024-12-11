from datetime import datetime
from sqlalchemy import Integer, String, Column, DateTime
from sqlalchemy.orm import relationship
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(225), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    # 添加与 Image 的关系
    images = relationship("Image", back_populates="user",
                          cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'username': self.username,
            'user_id': self.id,
            'created_at': datetime.timestamp(self.created_at) if self.created_at else None,
            'updated_at': datetime.timestamp(self.updated_at) if self.updated_at else None
        }
