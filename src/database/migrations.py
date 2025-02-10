#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库迁移脚本
提供数据库版本控制和迁移功能
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, Text
from sqlalchemy.sql import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect

from utils.logger import logger
from .models import Base

class DatabaseMigration:
    """数据库迁移管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库迁移管理器"""
        if db_path is None:
            # 默认数据库路径
            db_path = str(Path(__file__).parent.parent.parent / "data" / "writing_assistant.db")
        
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建数据库引擎
        self.engine = create_engine(f"sqlite:///{db_path}")
        
        # 创建版本控制表
        self._create_version_table()
    
    def _create_version_table(self):
        """创建版本控制表"""
        metadata = MetaData()
        
        # 定义版本控制表
        version_table = Table(
            'db_version',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('version', Integer, nullable=False),
            Column('description', String(200)),
            Column('applied_at', DateTime, default=datetime.utcnow)
        )
        
        # 检查表是否存在
        inspector = inspect(self.engine)
        if 'db_version' not in inspector.get_table_names():
            metadata.create_all(self.engine, tables=[version_table])
            # 插入初始版本
            with self.engine.connect() as conn:
                conn.execute(
                    version_table.insert().values(
                        version=1,
                        description="初始数据库结构"
                    )
                )
                conn.commit()
    
    def get_current_version(self) -> int:
        """获取当前数据库版本"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT version FROM db_version ORDER BY version DESC LIMIT 1")
                )
                version = result.scalar()
                return version if version is not None else 0
        except SQLAlchemyError as e:
            logger.error(f"获取数据库版本失败: {e}")
            return 0
    
    def migrate(self, target_version: Optional[int] = None) -> bool:
        """执行数据库迁移"""
        current_version = self.get_current_version()
        
        if target_version is None:
            # 如果未指定目标版本，则迁移到最新版本
            target_version = len(self._get_migrations())
        
        try:
            if current_version < target_version:
                # 向上迁移
                for version in range(current_version + 1, target_version + 1):
                    self._up_migration(version)
            elif current_version > target_version:
                # 向下迁移
                for version in range(current_version, target_version, -1):
                    self._down_migration(version)
            
            logger.info(f"数据库迁移成功: 从版本 {current_version} 到 {target_version}")
            return True
        except SQLAlchemyError as e:
            logger.error(f"数据库迁移失败: {e}")
            return False
    
    def _get_migrations(self) -> List[dict]:
        """获取所有迁移配置"""
        return [
            {
                'version': 1,
                'description': '初始数据库结构',
                'up': self._migration_v1_up,
                'down': self._migration_v1_down
            },
            {
                'version': 2,
                'description': '添加提示词模板字段',
                'up': self._migration_v2_up,
                'down': self._migration_v2_down
            },
            {
                'version': 3,
                'description': '添加AI对话历史表',
                'up': self._migration_v3_up,
                'down': self._migration_v3_down
            }
        ]
    
    def _migration_v1_up(self):
        """版本1迁移：创建初始表结构"""
        # 创建所有基础表
        Base.metadata.create_all(self.engine)
        
        # 初始化设置表
        inspector = inspect(self.engine)
        if 'settings' in inspector.get_table_names():
            with self.engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO settings (theme_mode)
                    SELECT 'light'
                    WHERE NOT EXISTS (SELECT 1 FROM settings);
                """))
                conn.commit()
    
    def _migration_v1_down(self):
        """版本1迁移回滚：删除所有表"""
        Base.metadata.drop_all(self.engine)
    
    def _migration_v2_up(self):
        """版本2迁移：添加提示词模板字段"""
        # 由于列已经在模型定义中，这里不需要再次添加
        logger.info("提示词模板字段已在模型定义中")
        
        # 确保settings表存在并包含必要的列
        inspector = inspect(self.engine)
        if 'settings' in inspector.get_table_names():
            with self.engine.connect() as conn:
                # 更新现有记录，设置默认值
                conn.execute(text("""
                    UPDATE settings 
                    SET generation_template = COALESCE(generation_template, ''),
                        continuation_template = COALESCE(continuation_template, '')
                    WHERE generation_template IS NULL 
                       OR continuation_template IS NULL;
                """))
                conn.commit()
    
    def _migration_v2_down(self):
        """版本2迁移回滚：删除提示词模板字段"""
        # 由于使用SQLite，且列已在模型定义中，这里不需要实际操作
        logger.info("提示词模板字段将在表重建时移除")
    
    def _migration_v3_up(self):
        """版本3迁移：添加AI对话历史表"""
        # 创建AI对话历史表
        metadata = MetaData()
        ai_dialog_history = Table(
            'ai_dialog_history',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('role', String(10), nullable=False),
            Column('content', Text, nullable=False),
            Column('created_at', DateTime, default=datetime.utcnow)
        )
        
        # 创建表
        inspector = inspect(self.engine)
        if 'ai_dialog_history' not in inspector.get_table_names():
            metadata.create_all(self.engine, tables=[ai_dialog_history])
            logger.info("AI对话历史表创建成功")
    
    def _migration_v3_down(self):
        """版本3迁移回滚：删除AI对话历史表"""
        metadata = MetaData()
        ai_dialog_history = Table(
            'ai_dialog_history',
            metadata,
            Column('id', Integer, primary_key=True)
        )
        
        # 删除表
        inspector = inspect(self.engine)
        if 'ai_dialog_history' in inspector.get_table_names():
            ai_dialog_history.drop(self.engine)
            logger.info("AI对话历史表删除成功")
    
    def _up_migration(self, version: int):
        """执行向上迁移"""
        migrations = self._get_migrations()
        migration = next((m for m in migrations if m['version'] == version), None)
        
        if migration:
            migration['up']()
            # 更新版本记录
            with self.engine.connect() as conn:
                conn.execute(
                    text("INSERT INTO db_version (version, description) VALUES (:version, :description)"),
                    {"version": version, "description": migration['description']}
                )
                conn.commit()
    
    def _down_migration(self, version: int):
        """执行向下迁移"""
        migrations = self._get_migrations()
        migration = next((m for m in migrations if m['version'] == version), None)
        
        if migration:
            migration['down']()
            # 删除版本记录
            with self.engine.connect() as conn:
                conn.execute(
                    text("DELETE FROM db_version WHERE version = :version"),
                    {"version": version}
                )
                conn.commit() 