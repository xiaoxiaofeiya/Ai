#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
编辑器组件
提供文本编辑功能，包括AI辅助写作功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, 
                           QPushButton, QHBoxLayout, QLabel,
                           QSpinBox, QProgressBar, QComboBox,
                           QDialog, QDialogButtonBox, QPlainTextEdit,
                           QInputDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont

from database.operations import DatabaseManager
from .ai_dialog import AIDialog

class PromptTemplateDialog(QDialog):
    """提示词模板编辑对话框"""
    
    def __init__(self, template: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("编辑提示词模板")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        help_text = """
可用的变量：
- {prompt}: 用户输入的提示词
- {context}: 已有内容（续写时使用）
- {genre}: 作品类型
- {style}: 写作风格
- {min_words}: 最小字数
- {max_words}: 最大字数
        """
        help_label = QLabel(help_text)
        help_label.setStyleSheet("color: #666666;")
        layout.addWidget(help_label)
        
        # 创建模板编辑器
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(template)
        layout.addWidget(self.editor)
        
        # 创建按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_template(self) -> str:
        """获取编辑后的模板"""
        return self.editor.toPlainText()

class Editor(QWidget):
    """编辑器组件"""
    
    # 定义信号
    content_changed = pyqtSignal(str)  # 内容变更信号
    ai_request = pyqtSignal(dict)       # AI请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Editor")
        self.current_chapter_id = None
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
        
        self._init_ui()
        
        # 加载提示词模板
        self._load_templates()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建工具栏
        toolbar = QWidget()
        toolbar.setObjectName("toolbar")
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建按钮组
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # AI生成按钮（新内容生成）
        generate_new_btn = QPushButton("生成")
        generate_new_btn.setObjectName("generateBtn")
        generate_new_btn.clicked.connect(self._generate_new_content)
        generate_new_btn.setEnabled(True)  # 新生成按钮默认启用
        self.generate_new_btn = generate_new_btn
        button_layout.addWidget(generate_new_btn)
        
        # AI续写按钮
        generate_btn = QPushButton("续写")
        generate_btn.setObjectName("continueBtn")
        generate_btn.clicked.connect(self._generate_content)
        generate_btn.setEnabled(False)
        self.generate_btn = generate_btn
        button_layout.addWidget(generate_btn)
        
        # 提示词模板按钮
        template_btn = QPushButton("提示词模板")
        template_btn.setObjectName("templateBtn")
        template_btn.clicked.connect(self._edit_template)
        self.template_btn = template_btn
        button_layout.addWidget(template_btn)
        
        toolbar_layout.addLayout(button_layout)
        
        # 生成字数设置
        toolbar_layout.addWidget(QLabel("生成字数:"))
        word_count = QSpinBox()
        word_count.setMinimum(100)
        word_count.setMaximum(2000)
        word_count.setValue(500)
        word_count.setSingleStep(100)
        self.word_count = word_count
        toolbar_layout.addWidget(word_count)
        
        # 进度条
        progress_bar = QProgressBar()
        progress_bar.setMaximumWidth(200)
        progress_bar.hide()
        self.progress_bar = progress_bar
        toolbar_layout.addWidget(progress_bar)
        
        toolbar_layout.addStretch()
        layout.addWidget(toolbar)
        
        # 创建编辑器
        editor = QTextEdit()
        editor.setPlaceholderText('在这里开始写作，或点击"生成"按钮生成内容...')
        editor.textChanged.connect(self._on_content_changed)
        self.editor = editor
        layout.addWidget(editor)
        
        # 设置布局
        self.setLayout(layout)
    
    def _load_templates(self):
        """从数据库加载提示词模板"""
        generation_template, continuation_template = self.db.get_prompt_templates()
        self.generation_template = generation_template
        self.continuation_template = continuation_template
    
    def _edit_template(self):
        """编辑提示词模板"""
        settings = self.db.get_settings()
        if not settings:
            return
            
        # 获取当前模板
        current_template = settings.generation_template or ""
        
        # 打开模板编辑对话框
        template, ok = QInputDialog.getMultiLineText(
            self,
            "编辑提示词模板",
            "请输入您的提示词模板:",
            current_template
        )
        
        if ok:
            # 更新数据库中的模板
            self.db.update_settings(generation_template=template)
            
    def _generate_new_content(self):
        """生成新内容"""
        # 创建并显示AI对话框
        dialog = AIDialog(self)
        dialog.content_generated.connect(self._insert_generated_content)
        dialog.exec()
    
    def _generate_content(self):
        """续写内容"""
        # 获取当前内容作为上下文
        cursor = self.editor.textCursor()
        context = self.editor.toPlainText()[:cursor.position()]
        
        # 创建并显示AI对话框
        dialog = AIDialog(self, context=context)
        dialog.content_generated.connect(self._insert_generated_content)
        dialog.exec()
    
    def _insert_generated_content(self, content: str):
        """插入生成的内容
        
        Args:
            content: 生成的内容
        """
        if not content:
            return
        
        # 在光标位置插入生成的内容
        cursor = self.editor.textCursor()
        cursor.insertText(content)
        
        # 发送内容变更信号
        self._on_content_changed()
    
    def set_chapter(self, chapter_id: int, content: str = ""):
        """设置当前章节"""
        self.current_chapter_id = chapter_id
        self.editor.setPlainText(content)
        self.generate_btn.setEnabled(True)  # 启用续写按钮
        self.generate_new_btn.setEnabled(True)  # 确保生成按钮也启用
    
    def _on_content_changed(self):
        """处理内容变更事件"""
        if self.current_chapter_id:
            content = self.editor.toPlainText()
            self.content_changed.emit(content)
    
    def get_content(self) -> str:
        """获取编辑器内容"""
        return self.editor.toPlainText()
    
    def set_content(self, content: str):
        """设置编辑器内容"""
        self.editor.setPlainText(content)
    
    def clear_content(self):
        """清空编辑器内容"""
        self.editor.clear()
        self.current_chapter_id = None
        self.generate_btn.setEnabled(False)  # 禁用续写按钮
        self.generate_new_btn.setEnabled(False)  # 禁用生成按钮
