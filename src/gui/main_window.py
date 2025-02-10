#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
主窗口模块
实现了应用程序的主要窗口界面，包括：
1. 项目列表（左侧栏）
2. 章节列表（中间栏）
3. 编辑区域（右侧栏）
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                           QVBoxLayout, QMenuBar, QMenu, QToolBar, 
                           QStatusBar, QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QProcess
import sys
from pathlib import Path
from datetime import datetime

from database.operations import DatabaseManager
from database.migrations import DatabaseMigration
from .settings_dialog import SettingsDialog
from .project_list import ProjectList
from .chapter_list import ChapterList
from .editor import Editor
from ai_services.deepseek import DeepSeekAIService
from ai_services.prompt import PromptTemplate

class MainWindow(QMainWindow):
    """主窗口类"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI写作助手")
        self.setMinimumSize(1200, 800)
        
        # 初始化数据库
        self._init_database()
        
        # 初始化UI组件
        self._init_ui()
        
        # 连接信号
        self._connect_signals()
        
        # 加载初始数据
        self._load_initial_data()
    
    def _init_database(self):
        """初始化数据库"""
        # 执行数据库迁移
        migration = DatabaseMigration()
        migration.migrate()
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
    
    def _load_initial_data(self):
        """加载初始数据"""
        # 加载设置
        settings = self.db.get_settings()
        if settings and settings.last_project_id:
            # 加载上次打开的项目
            self.project_list.select_project(settings.last_project_id)
        
        # 加载项目列表
        projects = self.db.get_all_projects()
        for project in projects:
            self.project_list.add_project(project.id, project.name)
    
    def _init_ui(self):
        """初始化UI组件"""
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建三个主要组件
        self.project_list = ProjectList()
        self.chapter_list = ChapterList()
        self.editor = Editor()
        
        # 添加到主布局
        main_layout.addWidget(self.project_list)
        main_layout.addWidget(self.chapter_list)
        main_layout.addWidget(self.editor)
        
        # 设置布局的伸缩因子
        main_layout.setStretch(0, 1)  # 项目列表
        main_layout.setStretch(1, 2)  # 章节列表
        main_layout.setStretch(2, 7)  # 编辑区域
        
        # 创建菜单栏
        self._create_menu_bar()
        
        # 创建工具栏
        self._create_tool_bar()
        
        # 创建状态栏
        self._create_status_bar()
    
    def _create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        new_project_action = QAction("新建项目", self)
        new_project_action.setShortcut("Ctrl+N")
        new_project_action.triggered.connect(self.project_list._create_new_project)
        file_menu.addAction(new_project_action)
        
        # 添加导出菜单
        export_menu = file_menu.addMenu("导出")
        backup_action = QAction("备份数据库", self)
        backup_action.triggered.connect(self._backup_database)
        export_menu.addAction(backup_action)
        
        restore_action = QAction("从备份恢复", self)
        restore_action.triggered.connect(self._restore_database)
        export_menu.addAction(restore_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑")
        
        # 视图菜单
        view_menu = menubar.addMenu("视图")
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        ai_settings_action = QAction("AI设置(&A)", self)
        ai_settings_action.setShortcut("Ctrl+,")
        ai_settings_action.setStatusTip("配置AI模型和API密钥")
        ai_settings_action.triggered.connect(self._show_settings_dialog)
        settings_menu.addAction(ai_settings_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)
    
    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)
        
        # 添加新建项目按钮
        new_project_action = QAction("新建项目", self)
        new_project_action.triggered.connect(self.project_list._create_new_project)
        toolbar.addAction(new_project_action)
        
        # 添加保存按钮
        save_action = QAction("保存", self)
        save_action.triggered.connect(self._save_current_chapter)
        toolbar.addAction(save_action)
        
        # 添加分隔符
        toolbar.addSeparator()
        
        # 添加设置按钮
        settings_action = QAction("AI设置", self)
        settings_action.setStatusTip("配置AI模型和API密钥")
        settings_action.triggered.connect(self._show_settings_dialog)
        toolbar.addAction(settings_action)
    
    def _create_status_bar(self):
        """创建状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.showMessage("就绪")
    
    def _connect_signals(self):
        """连接信号"""
        # 项目列表信号
        self.project_list.project_selected.connect(self._on_project_selected)
        self.project_list.project_created.connect(self._on_project_created)
        self.project_list.project_deleted.connect(self._on_project_deleted)
        self.project_list.project_renamed.connect(self._on_project_renamed)
        
        # 章节列表信号
        self.chapter_list.chapter_selected.connect(self._on_chapter_selected)
        self.chapter_list.chapter_created.connect(self._on_chapter_created)
        self.chapter_list.chapter_deleted.connect(self._on_chapter_deleted)
        self.chapter_list.chapter_renamed.connect(self._on_chapter_renamed)
        self.chapter_list.chapters_reordered.connect(self._on_chapters_reordered)
        
        # 编辑器信号
        self.editor.content_changed.connect(self._on_content_changed)
        self.editor.ai_request.connect(self._on_ai_request)
    
    def _show_settings_dialog(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()
    
    def _show_about_dialog(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "关于 AI写作助手",
            "AI写作助手 v1.0.0\n\n"
            "一个基于AI的智能写作辅助工具\n"
            "支持多种AI模型，提供智能写作建议"
        )
    
    def _save_current_chapter(self):
        """保存当前章节"""
        if self.editor.current_chapter_id:
            content = self.editor.get_content()
            if self.db.update_chapter(self.editor.current_chapter_id, content=content):
                self.statusBar().showMessage("保存成功", 3000)
    
    # 项目相关的槽函数
    def _on_project_selected(self, project_id: int):
        """处理项目选中事件"""
        project = self.db.get_project(project_id)
        if project:
            # 设置当前项目
            self.chapter_list.set_project(project_id, project.name)
            
            # 更新最后打开的项目
            self.db.update_settings(last_project_id=project_id)
            
            # 清空编辑器内容
            self.editor.clear_content()
    
    def _on_project_created(self, project_id: int):
        """处理项目创建事件"""
        project = self.db.get_project(project_id)
        if project:
            self.statusBar().showMessage(f"项目 '{project.name}' 创建成功", 3000)
    
    def _on_project_deleted(self, project_id: int):
        """处理项目删除事件"""
        if self.db.delete_project(project_id):
            self.chapter_list.clear_chapters()
            self.editor.clear_content()
            self.statusBar().showMessage("项目删除成功", 3000)
    
    def _on_project_renamed(self, project_id: int, new_name: str):
        """处理项目重命名事件"""
        if self.db.update_project(project_id, name=new_name):
            self.statusBar().showMessage(f"项目重命名为 '{new_name}'", 3000)
    
    # 章节相关的槽函数
    def _on_chapter_selected(self, chapter_id: int):
        """处理章节选中事件"""
        chapter = self.db.get_chapter(chapter_id)
        if chapter:
            self.editor.set_chapter(chapter_id, chapter.content or "")
    
    def _on_chapter_created(self, chapter_id: int):
        """处理章节创建事件"""
        chapter = self.db.get_chapter(chapter_id)
        if chapter:
            self.statusBar().showMessage(f"章节 '{chapter.title}' 创建成功", 3000)
    
    def _on_chapter_deleted(self, chapter_id: int):
        """处理章节删除事件"""
        if self.db.delete_chapter(chapter_id):
            self.editor.clear_content()
            self.statusBar().showMessage("章节删除成功", 3000)
    
    def _on_chapter_renamed(self, chapter_id: int, new_name: str):
        """处理章节重命名事件"""
        if self.db.update_chapter(chapter_id, title=new_name):
            self.statusBar().showMessage(f"章节重命名为 '{new_name}'", 3000)
    
    def _on_chapters_reordered(self):
        """处理章节重新排序事件"""
        # TODO: 实现章节重新排序的数据库操作
        self.statusBar().showMessage("章节顺序已更新", 3000)
    
    # 编辑器相关的槽函数
    def _on_content_changed(self, content: str):
        """处理内容变更事件"""
        if self.editor.current_chapter_id:
            # 自动保存内容
            self.db.update_chapter(self.editor.current_chapter_id, content=content)
    
    def _on_ai_request(self, request: dict):
        """处理AI请求"""
        dialog = request.get("dialog")
        if not dialog:
            return
            
        # 调用AI服务生成内容
        try:
            generated_content = self._generate_content(request)
            dialog.handle_ai_response({"text": generated_content})
            self.editor._insert_generated_content(generated_content)
        except Exception as e:
            dialog.handle_ai_response({"error": str(e)})

    def _generate_content(self, request: dict) -> str:
        """生成AI内容
        
        Args:
            request: 请求参数字典，包含：
                - type: 请求类型（"generate" 或 "continue"）
                - prompt: 提示词
                - word_count: 生成字数
                - context: 上下文内容（续写时使用）
                
        Returns:
            生成的内容
        """
        # 获取 API 设置
        settings = self.db.get_settings()
        if not settings or not settings.api_key:
            raise ValueError("请先在设置中配置 API 密钥")

        # 创建 AI 服务实例
        ai_service = DeepSeekAIService(
            api_key=settings.api_key,
            model="Pro/deepseek-ai/DeepSeek-R1",
            api_url="https://api.siliconflow.cn/v1/chat/completions"
        )
        
        # 准备提示词
        if request["type"] == "generate":
            # 使用生成内容的提示词模板
            prompt = PromptTemplate.get_generation_prompt(
                prompt=request["prompt"],
                custom_template=settings.generation_template,
                min_words=request["word_count"],
                max_words=request["word_count"] + 200
            )
        else:
            # 使用续写的提示词模板
            prompt = PromptTemplate.get_continuation_prompt(
                context=request.get("context", ""),
                custom_template=settings.continuation_template,
                min_words=request["word_count"],
                max_words=request["word_count"] + 200
            )
            prompt += f"\n\n用户提示：{request['prompt']}"
        
        # 调用 AI 服务生成内容
        try:
            result = ai_service.generate_content(prompt)
            if "error" in result:
                raise Exception(result["error"])
            return result["text"]
        except Exception as e:
            raise Exception(f"AI 内容生成失败：{str(e)}")

    def _backup_database(self):
        """备份数据库"""
        backup_path = self.db.backup_database()
        if backup_path:
            QMessageBox.information(
                self,
                "备份成功",
                f"数据库已备份到：\n{backup_path}\n\n同时生成了JSON格式的备份文件。"
            )
        else:
            QMessageBox.warning(
                self,
                "备份失败",
                "数据库备份失败，请查看日志了解详细信息。"
            )
    
    def _restore_database(self):
        """从备份恢复数据库"""
        # 获取备份目录
        backup_dir = Path(self.db.db_path).parent / "backups"
        if not backup_dir.exists():
            QMessageBox.warning(
                self,
                "恢复失败",
                "未找到备份目录。"
            )
            return
        
        # 获取所有备份文件
        backup_files = sorted(
            [f for f in backup_dir.glob("*.db")],
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if not backup_files:
            QMessageBox.warning(
                self,
                "恢复失败",
                "未找到备份文件。"
            )
            return
        
        # 选择备份文件
        items = [f"{f.name} ({datetime.fromtimestamp(f.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')})"
                for f in backup_files]
        item, ok = QInputDialog.getItem(
            self,
            "选择备份文件",
            "请选择要恢复的备份文件：",
            items,
            0,
            False
        )
        
        if ok and item:
            # 获取选中的备份文件
            index = items.index(item)
            backup_path = backup_files[index]
            
            # 确认恢复
            reply = QMessageBox.question(
                self,
                "确认恢复",
                "恢复数据库将覆盖当前所有数据，确定要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.db.restore_database(str(backup_path)):
                    QMessageBox.information(
                        self,
                        "恢复成功",
                        "数据库已成功恢复。\n程序将重新启动以加载恢复的数据。"
                    )
                    # 重启应用
                    QApplication.quit()
                    QProcess.startDetached(sys.executable, sys.argv)
                else:
                    QMessageBox.warning(
                        self,
                        "恢复失败",
                        "数据库恢复失败，请查看日志了解详细信息。"
                    )
