#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
章节列表组件
显示当前项目的所有章节，支持章节的创建、删除、重命名和排序等操作
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                           QListWidgetItem, QPushButton, QInputDialog,
                           QMessageBox, QMenu, QLabel)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from database.operations import DatabaseManager

class ChapterList(QWidget):
    """章节列表组件"""
    
    # 定义信号
    chapter_selected = pyqtSignal(int)  # 章节选中信号，参数为章节ID
    chapter_created = pyqtSignal(int)   # 章节创建信号，参数为新章节ID
    chapter_deleted = pyqtSignal(int)   # 章节删除信号，参数为被删除的章节ID
    chapter_renamed = pyqtSignal(int, str)  # 章节重命名信号，参数为章节ID和新名称
    chapters_reordered = pyqtSignal()   # 章节重新排序信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ChapterList")
        self.current_project_id = None
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 项目标题
        self.project_title = QLabel("未选择项目")
        self.project_title.setObjectName("projectTitle")
        layout.addWidget(self.project_title)
        
        # 创建新章节按钮
        new_chapter_btn = QPushButton("新建章节")
        new_chapter_btn.setObjectName("newChapterBtn")
        new_chapter_btn.clicked.connect(self._create_new_chapter)
        new_chapter_btn.setEnabled(False)
        self.new_chapter_btn = new_chapter_btn
        layout.addWidget(new_chapter_btn)
        
        # 创建章节列表
        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.list_widget.itemClicked.connect(self._on_chapter_selected)
        self.list_widget.model().rowsMoved.connect(self._on_chapters_reordered)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        
        # 设置布局
        self.setLayout(layout)
    
    def set_project(self, project_id: int, project_name: str):
        """设置当前项目"""
        # 清空当前章节列表
        self.clear_chapters()
        
        # 设置新项目
        self.current_project_id = project_id
        self.project_title.setText(project_name)
        self.new_chapter_btn.setEnabled(True)
        
        # 从数据库加载章节列表
        chapters = self.db.get_project_chapters(project_id)
        for chapter in chapters:
            self.add_chapter(chapter.id, chapter.title)
    
    def _create_new_chapter(self):
        """创建新章节"""
        if not self.current_project_id:
            return
            
        name, ok = QInputDialog.getText(
            self,
            "新建章节",
            "请输入章节名称:",
            text=f"第{self.list_widget.count() + 1}章"
        )
        
        if ok and name:
            # 调用数据库接口创建新章节
            chapter = self.db.create_chapter(self.current_project_id, name)
            if chapter:
                # 创建列表项
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, chapter.id)
                self.list_widget.addItem(item)
                
                # 发送章节创建信号
                self.chapter_created.emit(chapter.id)
    
    def _on_chapter_selected(self, item):
        """处理章节选中事件"""
        chapter_id = item.data(Qt.ItemDataRole.UserRole)
        self.chapter_selected.emit(chapter_id)
    
    def _on_chapters_reordered(self):
        """处理章节重新排序事件"""
        if not self.current_project_id:
            return
        
        # 收集所有章节的新顺序
        chapter_orders = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            chapter_orders.append({
                'id': item.data(Qt.ItemDataRole.UserRole),
                'order': i
            })
        
        # 更新数据库中的章节顺序
        if self.db.update_chapter_order(self.current_project_id, chapter_orders):
            self.chapters_reordered.emit()
        else:
            # 如果更新失败，重新加载章节列表
            self.set_project(self.current_project_id, self.project_title.text())
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.list_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 重命名操作
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self._rename_chapter(item))
        menu.addAction(rename_action)
        
        # 删除操作
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_chapter(item))
        menu.addAction(delete_action)
        
        # 显示菜单
        menu.exec(self.list_widget.mapToGlobal(position))
    
    def _rename_chapter(self, item):
        """重命名章节"""
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "重命名章节",
            "请输入新的章节名称:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            chapter_id = item.data(Qt.ItemDataRole.UserRole)
            # 更新数据库
            if self.db.update_chapter(chapter_id, title=new_name):
                item.setText(new_name)
                self.chapter_renamed.emit(chapter_id, new_name)
    
    def _delete_chapter(self, item):
        """删除章节"""
        reply = QMessageBox.question(
            self,
            "删除章节",
            f'确定要删除章节"{item.text()}"吗？\n此操作不可撤销。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            chapter_id = item.data(Qt.ItemDataRole.UserRole)
            # 从数据库删除
            if self.db.delete_chapter(chapter_id):
                self.list_widget.takeItem(self.list_widget.row(item))
                self.chapter_deleted.emit(chapter_id)
    
    def add_chapter(self, chapter_id: int, name: str):
        """添加章节到列表"""
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, chapter_id)
        self.list_widget.addItem(item)
    
    def clear_chapters(self):
        """清空章节列表"""
        self.list_widget.clear()
        if not self.current_project_id:  # 只有在没有选中项目时才重置标题
            self.project_title.setText("未选择项目")
            self.new_chapter_btn.setEnabled(False)
        self.current_project_id = None
