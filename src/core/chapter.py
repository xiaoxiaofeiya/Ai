#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
章节管理核心逻辑
处理章节的创建、更新、删除和排序等业务逻辑
"""

from typing import Optional, List, Dict, Any

from database.operations import DatabaseManager
from utils.logger import logger

class ChapterManager:
    """章节管理类"""
    
    def __init__(self):
        """初始化章节管理器"""
        self.db = DatabaseManager()
    
    def create_chapter(self, project_id: int, title: str, 
                      content: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """创建新章节
        
        Args:
            project_id: 项目ID
            title: 章节标题
            content: 章节内容
            
        Returns:
            章节信息字典或None（如果创建失败）
        """
        # 验证章节标题
        if not title or len(title.strip()) == 0:
            logger.error("章节标题不能为空")
            return None
        
        # 获取当前项目的章节数，用于设置order
        chapters = self.db.get_project_chapters(project_id)
        next_order = len(chapters)
        
        # 创建章节
        chapter = self.db.create_chapter(
            project_id=project_id,
            title=title.strip(),
            content=content
        )
        if not chapter:
            return None
        
        # 更新章节顺序
        self.db.update_chapter(chapter.id, order=next_order)
        
        return {
            'id': chapter.id,
            'title': chapter.title,
            'content': chapter.content,
            'order': next_order,
            'created_at': chapter.created_at,
            'updated_at': chapter.updated_at
        }
    
    def get_chapter(self, chapter_id: int) -> Optional[Dict[str, Any]]:
        """获取章节信息
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            章节信息字典或None（如果章节不存在）
        """
        chapter = self.db.get_chapter(chapter_id)
        if not chapter:
            return None
            
        return {
            'id': chapter.id,
            'project_id': chapter.project_id,
            'title': chapter.title,
            'content': chapter.content,
            'order': chapter.order,
            'created_at': chapter.created_at,
            'updated_at': chapter.updated_at
        }
    
    def get_project_chapters(self, project_id: int) -> List[Dict[str, Any]]:
        """获取项目的所有章节
        
        Args:
            project_id: 项目ID
            
        Returns:
            章节信息列表
        """
        chapters = self.db.get_project_chapters(project_id)
        return [
            {
                'id': chapter.id,
                'title': chapter.title,
                'content': chapter.content,
                'order': chapter.order,
                'created_at': chapter.created_at,
                'updated_at': chapter.updated_at
            }
            for chapter in chapters
        ]
    
    def update_chapter(self, chapter_id: int, title: Optional[str] = None,
                      content: Optional[str] = None) -> bool:
        """更新章节信息
        
        Args:
            chapter_id: 章节ID
            title: 新的章节标题
            content: 新的章节内容
            
        Returns:
            更新是否成功
        """
        update_data = {}
        if title is not None and len(title.strip()) > 0:
            update_data['title'] = title.strip()
        if content is not None:
            update_data['content'] = content
        
        if not update_data:
            logger.warning("没有需要更新的章节信息")
            return False
        
        return self.db.update_chapter(chapter_id, **update_data)
    
    def delete_chapter(self, chapter_id: int) -> bool:
        """删除章节
        
        Args:
            chapter_id: 章节ID
            
        Returns:
            删除是否成功
        """
        chapter = self.db.get_chapter(chapter_id)
        if not chapter:
            return False
        
        # 删除章节
        if not self.db.delete_chapter(chapter_id):
            return False
        
        # 重新排序剩余章节
        self._reorder_chapters(chapter.project_id)
        return True
    
    def update_chapter_order(self, project_id: int, chapter_orders: List[Dict[str, int]]) -> bool:
        """更新章节顺序
        
        Args:
            project_id: 项目ID
            chapter_orders: 章节顺序列表，格式为[{'id': chapter_id, 'order': new_order}, ...]
            
        Returns:
            更新是否成功
        """
        return self.db.update_chapter_order(project_id, chapter_orders)
    
    def _reorder_chapters(self, project_id: int):
        """重新排序项目的所有章节"""
        chapters = self.db.get_project_chapters(project_id)
        chapter_orders = [
            {'id': chapter.id, 'order': i}
            for i, chapter in enumerate(chapters)
        ]
        self.db.update_chapter_order(project_id, chapter_orders)
    
    def generate_content(self, chapter_id: int, prompt: Optional[str] = None) -> Optional[str]:
        """使用AI生成章节内容
        
        Args:
            chapter_id: 章节ID
            prompt: 生成提示词
            
        Returns:
            生成的内容或None（如果生成失败）
        """
        # TODO: 实现AI内容生成
        # 这里需要调用AI服务模块
        return None
    
    def continue_writing(self, chapter_id: int, context: str) -> Optional[str]:
        """使用AI续写章节内容
        
        Args:
            chapter_id: 章节ID
            context: 上下文内容
            
        Returns:
            生成的内容或None（如果生成失败）
        """
        # TODO: 实现AI续写
        # 这里需要调用AI服务模块
        return None
