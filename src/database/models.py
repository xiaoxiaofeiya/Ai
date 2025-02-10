#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库模型定义
使用 SQLAlchemy ORM 定义数据表结构
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    ForeignKey, create_engine
)
from sqlalchemy.orm import (
    declarative_base, relationship,
    sessionmaker, Session
)
from sqlalchemy.sql import func

Base = declarative_base()

class Project(Base):
    """项目表"""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    chapters = relationship("Chapter", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}')>"

class Chapter(Base):
    """章节表"""
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    prompt = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # 关系
    project = relationship("Project", back_populates="chapters")
    
    def __repr__(self):
        return f"<Chapter(id={self.id}, title='{self.title}', order={self.order})>"

class Settings(Base):
    """设置表"""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    api_key = Column(String(100))
    theme_mode = Column(String(10), default='light')
    last_project_id = Column(Integer, ForeignKey('projects.id'))
    
    # 新增字段：提示词模板
    generation_template = Column(Text)  # 生成内容的提示词模板
    continuation_template = Column(Text)  # 续写的提示词模板
    
    def __repr__(self):
        return f"<Settings(id={self.id}, theme_mode='{self.theme_mode}')>"

class AIDialogHistory(Base):
    """AI对话历史表"""
    __tablename__ = 'ai_dialog_history'
    
    id = Column(Integer, primary_key=True)
    role = Column(String(10), nullable=False)  # 'user' 或 'ai'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<AIDialogHistory(id={self.id}, role='{self.role}')>"
