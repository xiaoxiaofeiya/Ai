#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置对话框
"""

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QComboBox, QLineEdit, QPushButton, QGroupBox,
                           QFormLayout, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal

import yaml
from pathlib import Path

from database.operations import DatabaseManager
from ai_services.deepseek import DeepSeekAIService

class SettingsDialog(QDialog):
    """设置对话框"""
    
    # 定义信号
    settings_updated = pyqtSignal(dict)  # 设置更新信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        
        # 创建数据库管理器实例
        self.db = DatabaseManager()
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化UI
        self._init_ui()
        
        # 加载当前设置
        self._load_current_settings()
    
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # AI模型设置组
        ai_group = QGroupBox("AI模型设置")
        ai_layout = QFormLayout()
        
        # 模型提供商选择
        self.provider_combo = QComboBox()
        for model in self.config["ai_services"]["supported_models"]:
            self.provider_combo.addItem(model["name"], model["key"])
        self.provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        ai_layout.addRow("选择模型:", self.provider_combo)
        
        # 具体模型选择
        self.model_combo = QComboBox()
        self._update_model_list()
        ai_layout.addRow("模型版本:", self.model_combo)
        
        # API密钥输入
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        ai_layout.addRow("API密钥:", self.api_key_input)
        
        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self._test_connection)
        ai_layout.addRow("", self.test_btn)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        save_btn.clicked.connect(self._save_settings)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _load_config(self):
        """加载配置文件"""
        config_path = Path("config/config.yaml")
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    return config if config else {
                        "ai_services": {
                            "supported_models": [
                                {
                                    "name": "DeepSeek",
                                    "key": "deepseek",
                                    "api_url": "https://api.siliconflow.cn/v1/chat/completions",
                                    "models": ["Pro/deepseek-ai/DeepSeek-R1"]
                                }
                            ],
                            "default": {
                                "provider": "deepseek",
                                "model": "Pro/deepseek-ai/DeepSeek-R1"
                            }
                        }
                    }
            except Exception as e:
                print(f"加载配置文件失败: {e}")
        return {
            "ai_services": {
                "supported_models": [
                    {
                        "name": "DeepSeek",
                        "key": "deepseek",
                        "api_url": "https://api.siliconflow.cn/v1/chat/completions",
                        "models": ["Pro/deepseek-ai/DeepSeek-R1"]
                    }
                ],
                "default": {
                    "provider": "deepseek",
                    "model": "Pro/deepseek-ai/DeepSeek-R1"
                }
            }
        }
    
    def _load_current_settings(self):
        """加载当前设置"""
        settings = self.db.get_settings()
        if settings:
            # 设置API密钥
            if settings.api_key:
                self.api_key_input.setText(settings.api_key)
            
            # 设置提供商和模型
            provider = self.config["ai_services"]["default"]["provider"]
            model = self.config["ai_services"]["default"]["model"]
            
            # 设置当前选中的提供商
            index = self.provider_combo.findData(provider)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)
            
            # 设置当前选中的模型
            index = self.model_combo.findText(model)
            if index >= 0:
                self.model_combo.setCurrentIndex(index)
    
    def _on_provider_changed(self, index):
        """当模型提供商改变时更新模型列表"""
        self._update_model_list()
    
    def _update_model_list(self):
        """更新模型列表"""
        self.model_combo.clear()
        current_provider = self.provider_combo.currentData()
        
        # 查找当前提供商的模型列表
        for provider in self.config["ai_services"]["supported_models"]:
            if provider["key"] == current_provider:
                self.model_combo.addItems(provider["models"])
                break
    
    def _test_connection(self):
        """测试API连接"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        provider = self.provider_combo.currentData()
        model = self.model_combo.currentText()
        
        # 禁用测试按钮并显示状态
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        
        try:
            # 创建AI服务实例
            if provider == "deepseek":
                service = DeepSeekAIService(
                    api_key=api_key,
                    model=model,
                    api_url=self._get_provider_api_url(provider),
                    timeout=60  # 设置60秒超时
                )
                
                # 测试连接
                if service.validate_api_key():
                    QMessageBox.information(
                        self,
                        "连接成功",
                        "API连接测试成功！\n"
                        "• 服务器连接正常\n"
                        "• API密钥有效\n"
                        "• 模型可用"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "连接失败",
                        "API连接测试失败。\n"
                        "可能的原因：\n"
                        "• API密钥无效\n"
                        "• 账户余额不足\n"
                        "• 服务器暂时性错误\n\n"
                        "建议：\n"
                        "1. 检查API密钥是否正确\n"
                        "2. 确认账户状态\n"
                        "3. 稍后重试"
                    )
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                QMessageBox.warning(
                    self,
                    "连接超时",
                    "连接服务器超时。系统已尝试自动重试，但仍然失败。\n\n"
                    "可能的原因：\n"
                    "• 网络连接不稳定\n"
                    "• 服务器响应慢\n"
                    "• 防火墙拦截\n\n"
                    "建议：\n"
                    "1. 检查网络连接\n"
                    "2. 确认是否可以访问 api.siliconflow.cn\n"
                    "3. 检查防火墙设置\n"
                    "4. 稍后重试"
                )
            elif "connection" in error_msg.lower():
                QMessageBox.warning(
                    self,
                    "连接错误",
                    "无法连接到服务器。系统已尝试自动重试，但仍然失败。\n\n"
                    "可能的原因：\n"
                    "• 网络连接断开\n"
                    "• DNS解析失败\n"
                    "• 服务器暂时不可用\n\n"
                    "建议：\n"
                    "1. 检查网络连接\n"
                    "2. 尝试更换网络（如切换到手机热点）\n"
                    "3. 检查系统代理设置\n"
                    "4. 稍后重试"
                )
            else:
                QMessageBox.critical(
                    self,
                    "错误",
                    f"测试连接时发生错误：\n\n"
                    f"错误信息：{error_msg}\n\n"
                    f"建议：\n"
                    f"1. 检查网络连接\n"
                    f"2. 确认API密钥格式正确\n"
                    f"3. 稍后重试"
                )
        finally:
            # 恢复测试按钮状态
            self.test_btn.setEnabled(True)
            self.test_btn.setText("测试连接")
    
    def _get_provider_api_url(self, provider: str) -> str:
        """获取提供商的API URL"""
        for model in self.config["ai_services"]["supported_models"]:
            if model["key"] == provider:
                return model["api_url"]
        return ""
    
    def _save_settings(self):
        """保存设置"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        settings = {
            "api_key": api_key,
            "provider": self.provider_combo.currentData(),
            "model": self.model_combo.currentText()
        }
        
        # 更新数据库中的设置
        if self.db.update_settings(api_key=api_key):
            # 更新配置文件中的默认设置
            config_path = Path("config/config.yaml")
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                
                config["ai_services"]["default"]["provider"] = settings["provider"]
                config["ai_services"]["default"]["model"] = settings["model"]
                
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(config, f, allow_unicode=True)
            
            # 发送设置更新信号
            self.settings_updated.emit(settings)
            
            QMessageBox.information(self, "成功", "设置已保存")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "保存设置失败") 