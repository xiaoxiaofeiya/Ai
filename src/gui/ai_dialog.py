#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI对话框组件
提供与AI模型的对话界面
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QPushButton, QLabel, QSpinBox, QProgressBar,
                           QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from database.operations import DatabaseManager

class AIDialog(QDialog):
    """AI对话框"""
    
    # 定义信号
    content_generated = pyqtSignal(str)  # 内容生成信号，当用户确认采用生成的内容时发出
    
    def __init__(self, parent=None, context: str = ""):
        """初始化对话框
        
        Args:
            parent: 父窗口
            context: 当前文章内容（用于续写模式）
        """
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("AI助手")
        self.setMinimumSize(800, 600)
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
        
        self._init_ui()
        
        # 加载历史对话记录
        self._load_history()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 对话历史区域
        history_label = QLabel("对话历史")
        layout.addWidget(history_label)
        
        self.history_edit = QTextEdit()
        self.history_edit.setReadOnly(True)
        layout.addWidget(self.history_edit)
        
        # 输入区域
        input_label = QLabel("输入提示词")
        layout.addWidget(input_label)
        
        self.input_edit = QTextEdit()
        self.input_edit.setMaximumHeight(100)
        layout.addWidget(self.input_edit)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        # 字数设置
        control_layout.addWidget(QLabel("生成字数:"))
        self.word_count = QSpinBox()
        self.word_count.setMinimum(100)
        self.word_count.setMaximum(2000)
        self.word_count.setValue(500)
        self.word_count.setSingleStep(100)
        control_layout.addWidget(self.word_count)
        
        # 生成按钮
        self.generate_btn = QPushButton("生成")
        self.generate_btn.clicked.connect(self._on_generate)
        control_layout.addWidget(self.generate_btn)
        
        # 续写按钮（仅在有上下文时启用）
        self.continue_btn = QPushButton("续写")
        self.continue_btn.clicked.connect(self._on_continue)
        self.continue_btn.setEnabled(bool(self.context))
        control_layout.addWidget(self.continue_btn)
        
        # 清空按钮
        clear_btn = QPushButton("清空对话")
        clear_btn.clicked.connect(self._on_clear)
        control_layout.addWidget(clear_btn)
        
        control_layout.addStretch()
        
        # 采用按钮（默认禁用，直到生成了内容）
        self.adopt_btn = QPushButton("采用内容")
        self.adopt_btn.clicked.connect(self._on_adopt)
        self.adopt_btn.setEnabled(False)
        control_layout.addWidget(self.adopt_btn)
        
        layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(2)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # 存储最后生成的内容
        self.last_generated_content = ""
    
    def _load_history(self):
        """加载历史对话记录"""
        history_records = self.db.get_dialog_history()
        for record in history_records:
            self._add_to_history(
                "用户" if record.role == "user" else "AI",
                record.content,
                save_to_db=False  # 不需要再次保存到数据库
            )
    
    def _on_generate(self):
        """处理生成按钮点击事件"""
        prompt = self.input_edit.toPlainText().strip()
        if not prompt:
            return
            
        # 显示进度条
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.generate_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        
        # 添加用户输入到历史
        self._add_to_history("用户", prompt)
        
        # 发送AI请求
        self.parent().ai_request.emit({
            "type": "generate",
            "prompt": prompt,
            "word_count": self.word_count.value(),
            "dialog": self  # 传递对话框实例以便回调
        })
    
    def _on_continue(self):
        """处理续写按钮点击事件"""
        prompt = self.input_edit.toPlainText().strip()
        if not prompt:
            return
            
        # 显示进度条
        self.progress_bar.setRange(0, 0)
        self.progress_bar.show()
        self.generate_btn.setEnabled(False)
        self.continue_btn.setEnabled(False)
        
        # 添加用户输入到历史
        self._add_to_history("用户", prompt)
        
        # 发送AI请求
        self.parent().ai_request.emit({
            "type": "continue",
            "prompt": prompt,
            "context": self.context,
            "word_count": self.word_count.value(),
            "dialog": self  # 传递对话框实例以便回调
        })
    
    def _on_clear(self):
        """清空对话历史"""
        reply = QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有对话历史吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 清空数据库中的历史记录
            if self.db.clear_dialog_history():
                self.history_edit.clear()
                self.input_edit.clear()
                self.last_generated_content = ""
                self.adopt_btn.setEnabled(False)
            else:
                QMessageBox.warning(self, "错误", "清空对话历史失败")
    
    def _on_adopt(self):
        """采用生成的内容"""
        if self.last_generated_content:
            self.content_generated.emit(self.last_generated_content)
            self.accept()
    
    def _add_to_history(self, role: str, content: str, save_to_db: bool = True):
        """添加内容到对话历史
        
        Args:
            role: 角色（"用户"或"AI"）
            content: 内容
            save_to_db: 是否保存到数据库
        """
        cursor = self.history_edit.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        
        # 添加分隔线
        if self.history_edit.toPlainText():
            cursor.insertText("\n\n" + "-" * 50 + "\n\n")
        
        # 添加新内容
        cursor.insertText(f"{role}：\n{content}")
        
        # 滚动到底部
        cursor.movePosition(cursor.MoveOperation.End)
        self.history_edit.setTextCursor(cursor)
        
        # 保存到数据库
        if save_to_db:
            self.db.add_dialog_history(
                "user" if role == "用户" else "ai",
                content
            )
    
    def handle_ai_response(self, response: dict):
        """处理AI响应
        
        Args:
            response: AI响应数据
        """
        # 隐藏进度条
        self.progress_bar.hide()
        self.generate_btn.setEnabled(True)
        self.continue_btn.setEnabled(bool(self.context))
        
        if "error" in response:
            # 处理错误
            self._add_to_history("AI", f"错误：{response['error']}")
            self.last_generated_content = ""
            self.adopt_btn.setEnabled(False)
        else:
            # 处理成功响应
            content = response.get("text", "").strip()
            if content:
                self._add_to_history("AI", content)
                self.last_generated_content = content
                self.adopt_btn.setEnabled(True)
            else:
                self._add_to_history("AI", "生成的内容为空")
                self.last_generated_content = ""
                self.adopt_btn.setEnabled(False)
        
        # 清空输入框
        self.input_edit.clear() 