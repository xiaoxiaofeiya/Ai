#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
数据库操作
提供数据库的基本操作功能
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Any, Dict

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Base, Project, Chapter, Settings, AIDialogHistory
from utils.logger import logger

class DatabaseManager:
    """数据库管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初始化数据库管理器"""
        if db_path is None:
            # 默认数据库路径
            db_path = str(Path(__file__).parent.parent.parent / "data" / "writing_assistant.db")
        
        self.db_path = db_path
        # 确保数据库目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 创建数据库引擎
        self.engine = create_engine(f"sqlite:///{db_path}")
        
        # 创建会话工厂
        self.Session = sessionmaker(bind=self.engine)
        
        # 创建数据库表
        self._create_tables()
        
        # 初始化设置
        self._init_settings()
    
    def _create_tables(self):
        """创建数据库表"""
        Base.metadata.create_all(self.engine)
    
    def _init_settings(self):
        """初始化设置表"""
        with self.Session() as session:
            if not session.query(Settings).first():
                settings = Settings()
                session.add(settings)
                session.commit()
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.Session()
    
    # 项目相关操作
    def create_project(self, name: str, description: Optional[str] = None) -> Optional[Project]:
        """创建新项目"""
        try:
            with self.Session() as session:
                project = Project(name=name, description=description)
                session.add(project)
                session.commit()
                logger.info(f"创建项目成功: {project}")
                return project
        except SQLAlchemyError as e:
            logger.error(f"创建项目失败: {e}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """获取项目信息"""
        try:
            with self.Session() as session:
                return session.query(Project).get(project_id)
        except SQLAlchemyError as e:
            logger.error(f"获取项目失败: {e}")
            return None
    
    def get_all_projects(self) -> List[Project]:
        """获取所有项目"""
        try:
            with self.Session() as session:
                return session.query(Project).all()
        except SQLAlchemyError as e:
            logger.error(f"获取项目列表失败: {e}")
            return []
    
    def update_project(self, project_id: int, **kwargs) -> bool:
        """更新项目信息"""
        try:
            with self.Session() as session:
                project = session.query(Project).get(project_id)
                if project:
                    for key, value in kwargs.items():
                        setattr(project, key, value)
                    session.commit()
                    logger.info(f"更新项目成功: {project}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"更新项目失败: {e}")
            return False
    
    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        try:
            with self.Session() as session:
                project = session.query(Project).get(project_id)
                if project:
                    session.delete(project)
                    session.commit()
                    logger.info(f"删除项目成功: {project}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"删除项目失败: {e}")
            return False
    
    # 章节相关操作
    def create_chapter(self, project_id: int, title: str, content: Optional[str] = None) -> Optional[Chapter]:
        """创建新章节"""
        try:
            with self.Session() as session:
                chapter = Chapter(project_id=project_id, title=title, content=content)
                session.add(chapter)
                session.commit()
                logger.info(f"创建章节成功: {chapter}")
                return chapter
        except SQLAlchemyError as e:
            logger.error(f"创建章节失败: {e}")
            return None
    
    def get_chapter(self, chapter_id: int) -> Optional[Chapter]:
        """获取章节信息"""
        try:
            with self.Session() as session:
                return session.query(Chapter).get(chapter_id)
        except SQLAlchemyError as e:
            logger.error(f"获取章节失败: {e}")
            return None
    
    def get_project_chapters(self, project_id: int) -> List[Chapter]:
        """获取项目的所有章节，按order字段排序"""
        try:
            with self.Session() as session:
                return session.query(Chapter).filter_by(
                    project_id=project_id
                ).order_by(Chapter.order).all()
        except SQLAlchemyError as e:
            logger.error(f"获取章节列表失败: {e}")
            return []
    
    def update_chapter(self, chapter_id: int, **kwargs) -> bool:
        """更新章节信息"""
        try:
            with self.Session() as session:
                chapter = session.query(Chapter).get(chapter_id)
                if chapter:
                    for key, value in kwargs.items():
                        setattr(chapter, key, value)
                    session.commit()
                    logger.info(f"更新章节成功: {chapter}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"更新章节失败: {e}")
            return False
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """删除章节"""
        try:
            with self.Session() as session:
                chapter = session.query(Chapter).get(chapter_id)
                if chapter:
                    session.delete(chapter)
                    session.commit()
                    logger.info(f"删除章节成功: {chapter}")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"删除章节失败: {e}")
            return False
    
    def update_chapter_order(self, project_id: int, chapter_orders: List[Dict[str, int]]) -> bool:
        """更新章节顺序
        
        Args:
            project_id: 项目ID
            chapter_orders: 章节顺序列表，格式为[{'id': chapter_id, 'order': new_order}, ...]
        """
        try:
            with self.Session() as session:
                for order_info in chapter_orders:
                    chapter = session.query(Chapter).filter_by(
                        id=order_info['id'],
                        project_id=project_id
                    ).first()
                    if chapter:
                        chapter.order = order_info['order']
                session.commit()
                logger.info(f"更新章节顺序成功: project_id={project_id}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"更新章节顺序失败: {e}")
            return False
    
    # 设置相关操作
    def get_settings(self) -> Optional[Settings]:
        """获取应用设置"""
        try:
            with self.Session() as session:
                return session.query(Settings).first()
        except SQLAlchemyError as e:
            logger.error(f"获取设置失败: {e}")
            return None
    
    def update_settings(self, **kwargs) -> bool:
        """更新应用设置"""
        try:
            with self.Session() as session:
                settings = session.query(Settings).first()
                if settings:
                    for key, value in kwargs.items():
                        setattr(settings, key, value)
                    session.commit()
                    logger.info("更新设置成功")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"更新设置失败: {e}")
            return False
    
    def backup_database(self) -> Optional[str]:
        """备份数据库
        
        Returns:
            备份文件路径或None（如果备份失败）
        """
        try:
            # 创建备份目录
            backup_dir = Path(self.db_path).parent / "backups"
            backup_dir.mkdir(exist_ok=True)
            
            # 生成备份文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = backup_dir / f"writing_assistant_{timestamp}.db"
            
            # 复制数据库文件
            shutil.copy2(self.db_path, backup_path)
            
            # 导出项目数据为JSON（额外备份）
            json_backup_path = backup_dir / f"writing_assistant_{timestamp}.json"
            self._export_data_to_json(json_backup_path)
            
            logger.info(f"数据库备份成功: {backup_path}")
            return str(backup_path)
        except Exception as e:
            logger.error(f"数据库备份失败: {e}")
            return None
    
    def restore_database(self, backup_path: str) -> bool:
        """从备份恢复数据库
        
        Args:
            backup_path: 备份文件路径
        """
        try:
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 停止数据库连接
            self.engine.dispose()
            
            # 恢复数据库文件
            shutil.copy2(backup_path, self.db_path)
            
            # 重新创建数据库连接
            self.engine = create_engine(f"sqlite:///{self.db_path}")
            self.Session = sessionmaker(bind=self.engine)
            
            logger.info(f"数据库恢复成功: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"数据库恢复失败: {e}")
            return False
    
    def _export_data_to_json(self, json_path: str):
        """导出数据库数据为JSON格式"""
        try:
            with self.Session() as session:
                # 导出项目数据
                projects = session.query(Project).all()
                data = {
                    'projects': [],
                    'settings': None
                }
                
                # 收集项目和章节数据
                for project in projects:
                    project_data = {
                        'id': project.id,
                        'name': project.name,
                        'description': project.description,
                        'created_at': project.created_at.isoformat(),
                        'updated_at': project.updated_at.isoformat(),
                        'chapters': []
                    }
                    
                    for chapter in project.chapters:
                        chapter_data = {
                            'id': chapter.id,
                            'title': chapter.title,
                            'content': chapter.content,
                            'prompt': chapter.prompt,
                            'order': chapter.order,
                            'created_at': chapter.created_at.isoformat(),
                            'updated_at': chapter.updated_at.isoformat()
                        }
                        project_data['chapters'].append(chapter_data)
                    
                    data['projects'].append(project_data)
                
                # 导出设置数据
                settings = session.query(Settings).first()
                if settings:
                    data['settings'] = {
                        'api_key': settings.api_key,
                        'theme_mode': settings.theme_mode,
                        'last_project_id': settings.last_project_id,
                        'generation_template': settings.generation_template,
                        'continuation_template': settings.continuation_template
                    }
                
                # 写入JSON文件
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.info(f"数据导出成功: {json_path}")
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            raise

    def get_prompt_templates(self) -> tuple[Optional[str], Optional[str]]:
        """获取提示词模板
        
        Returns:
            (generation_template, continuation_template)元组
        """
        try:
            with self.Session() as session:
                settings = session.query(Settings).first()
                if settings:
                    return settings.generation_template, settings.continuation_template
                return None, None
        except SQLAlchemyError as e:
            logger.error(f"获取提示词模板失败: {e}")
            return None, None
    
    def update_prompt_templates(self, generation_template: Optional[str] = None,
                              continuation_template: Optional[str] = None) -> bool:
        """更新提示词模板
        
        Args:
            generation_template: 生成内容的提示词模板
            continuation_template: 续写的提示词模板
            
        Returns:
            更新是否成功
        """
        try:
            with self.Session() as session:
                settings = session.query(Settings).first()
                if settings:
                    if generation_template is not None:
                        settings.generation_template = generation_template
                    if continuation_template is not None:
                        settings.continuation_template = continuation_template
                    session.commit()
                    logger.info("更新提示词模板成功")
                    return True
                return False
        except SQLAlchemyError as e:
            logger.error(f"更新提示词模板失败: {e}")
            return False

    def add_dialog_history(self, role: str, content: str) -> Optional[AIDialogHistory]:
        """添加对话历史记录
        
        Args:
            role: 角色（'user' 或 'ai'）
            content: 对话内容
            
        Returns:
            Optional[AIDialogHistory]: 创建的记录或None
        """
        try:
            with self.Session() as session:
                history = AIDialogHistory(role=role, content=content)
                session.add(history)
                session.commit()
                logger.info(f"添加对话历史记录成功: {history}")
                return history
        except SQLAlchemyError as e:
            logger.error(f"添加对话历史记录失败: {e}")
            return None
    
    def get_dialog_history(self) -> List[AIDialogHistory]:
        """获取所有对话历史记录
        
        Returns:
            List[AIDialogHistory]: 对话历史记录列表
        """
        try:
            with self.Session() as session:
                return session.query(AIDialogHistory).order_by(AIDialogHistory.created_at).all()
        except SQLAlchemyError as e:
            logger.error(f"获取对话历史记录失败: {e}")
            return []
    
    def clear_dialog_history(self) -> bool:
        """清空对话历史记录
        
        Returns:
            bool: 是否清空成功
        """
        try:
            with self.Session() as session:
                session.query(AIDialogHistory).delete()
                session.commit()
                logger.info("清空对话历史记录成功")
                return True
        except SQLAlchemyError as e:
            logger.error(f"清空对话历史记录失败: {e}")
            return False
