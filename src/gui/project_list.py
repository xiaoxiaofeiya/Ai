#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
项目列表组件
显示所有创建的写作项目，支持项目的创建、删除、重命名等操作
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                           QListWidgetItem, QPushButton, QInputDialog,
                           QMessageBox, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

from database.operations import DatabaseManager

class ProjectList(QWidget):
    """项目列表组件"""
    
    # 定义信号
    project_selected = pyqtSignal(int)  # 项目选中信号，参数为项目ID
    project_created = pyqtSignal(int)   # 项目创建信号，参数为新项目ID
    project_deleted = pyqtSignal(int)   # 项目删除信号，参数为被删除的项目ID
    project_renamed = pyqtSignal(int, str)  # 项目重命名信号，参数为项目ID和新名称
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectList")
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
        
        self._init_ui()
        
        # 加载现有项目
        self._load_projects()
    
    def _load_projects(self):
        """加载现有项目"""
        projects = self.db.get_all_projects()
        for project in projects:
            self.add_project(project.id, project.name)
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建新项目按钮
        new_project_btn = QPushButton("新建项目")
        new_project_btn.setObjectName("newProjectBtn")
        new_project_btn.clicked.connect(self._create_new_project)
        layout.addWidget(new_project_btn)
        
        # 创建项目列表
        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self._on_project_selected)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self.list_widget)
        
        # 设置布局
        self.setLayout(layout)
    
    def _create_new_project(self):
        """创建新项目"""
        name, ok = QInputDialog.getText(
            self,
            "新建项目",
            "请输入项目名称:",
            text="未命名项目"
        )
        
        if ok and name:
            # 调用数据库接口创建新项目
            project = self.db.create_project(name)
            if project:
                # 创建列表项
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, project.id)
                self.list_widget.addItem(item)
                
                # 发送项目创建信号
                self.project_created.emit(project.id)
    
    def _on_project_selected(self, item):
        """处理项目选中事件"""
        project_id = item.data(Qt.ItemDataRole.UserRole)
        self.project_selected.emit(project_id)
    
    def _show_context_menu(self, position):
        """显示右键菜单"""
        item = self.list_widget.itemAt(position)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 重命名操作
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self._rename_project(item))
        menu.addAction(rename_action)
        
        # 删除操作
        delete_action = QAction("删除", self)
        delete_action.triggered.connect(lambda: self._delete_project(item))
        menu.addAction(delete_action)
        
        # 显示菜单
        menu.exec(self.list_widget.mapToGlobal(position))
    
    def _rename_project(self, item):
        """重命名项目"""
        old_name = item.text()
        new_name, ok = QInputDialog.getText(
            self,
            "重命名项目",
            "请输入新的项目名称:",
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            project_id = item.data(Qt.ItemDataRole.UserRole)
            # 更新数据库
            if self.db.update_project(project_id, name=new_name):
                item.setText(new_name)
                self.project_renamed.emit(project_id, new_name)
    
    def _delete_project(self, item):
        """删除项目"""
        reply = QMessageBox.question(
            self,
            "删除项目",
            f'确定要删除项目"{item.text()}"吗？\n此操作不可撤销。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            project_id = item.data(Qt.ItemDataRole.UserRole)
            # 从数据库删除
            if self.db.delete_project(project_id):
                self.list_widget.takeItem(self.list_widget.row(item))
                self.project_deleted.emit(project_id)
    
    def add_project(self, project_id: int, name: str):
        """添加项目到列表"""
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, project_id)
        self.list_widget.addItem(item)
    
    def clear_projects(self):
        """清空项目列表"""
        self.list_widget.clear()
    
    def select_project(self, project_id: int):
        """选中指定项目"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == project_id:
                self.list_widget.setCurrentItem(item)
                break
