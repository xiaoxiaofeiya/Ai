#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
设置管理核心逻辑
处理应用设置的读取和更新
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

from database.operations import DatabaseManager
from utils.logger import logger

class SettingsManager:
    """设置管理类"""
    
    def __init__(self):
        """初始化设置管理器"""
        self.db = DatabaseManager()
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        return {}
    
    def get_settings(self) -> Dict[str, Any]:
        """获取应用设置
        
        Returns:
            设置信息字典
        """
        settings = self.db.get_settings()
        if not settings:
            return {
                'api_key': None,
                'theme_mode': 'light',
                'last_project_id': None
            }
        
        return {
            'api_key': settings.api_key,
            'theme_mode': settings.theme_mode,
            'last_project_id': settings.last_project_id
        }
    
    def update_settings(self, **kwargs) -> bool:
        """更新应用设置
        
        Args:
            **kwargs: 设置项键值对
            
        Returns:
            更新是否成功
        """
        # 验证主题模式
        if 'theme_mode' in kwargs:
            theme_mode = kwargs['theme_mode']
            if theme_mode not in ['light', 'dark']:
                logger.error(f"不支持的主题模式: {theme_mode}")
                return False
        
        return self.db.update_settings(**kwargs)
    
    def get_ai_config(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """获取AI服务配置
        
        Args:
            provider: AI服务提供商，如果为None则返回默认配置
            
        Returns:
            AI服务配置字典
        """
        ai_config = self.config.get('ai_services', {})
        if not provider:
            provider = ai_config.get('default', {}).get('provider')
        
        # 获取提供商配置
        provider_config = None
        for model in ai_config.get('supported_models', []):
            if model['key'] == provider:
                provider_config = model
                break
        
        if not provider_config:
            return {}
        
        return {
            'provider': provider,
            'api_base_url': provider_config['api_base_url'],
            'models': provider_config['models'],
            'timeout': ai_config.get('default', {}).get('timeout', 30)
        }
    
    def get_export_config(self) -> Dict[str, Any]:
        """获取导出配置
        
        Returns:
            导出配置字典
        """
        export_config = self.config.get('export', {})
        return {
            'default_format': export_config.get('default_format', 'docx'),
            'output_dir': export_config.get('output_dir', 'exports')
        }
    
    def get_gui_config(self) -> Dict[str, Any]:
        """获取GUI配置
        
        Returns:
            GUI配置字典
        """
        gui_config = self.config.get('gui', {})
        return {
            'theme': gui_config.get('theme', 'light'),
            'window': gui_config.get('window', {
                'width': 1280,
                'height': 800,
                'title': "AI写作助手"
            }),
            'font': gui_config.get('font', {
                'family': "Microsoft YaHei",
                'size': 12
            })
        }
    
    def validate_api_key(self, api_key: str, provider: str) -> bool:
        """验证API密钥
        
        Args:
            api_key: API密钥
            provider: AI服务提供商
            
        Returns:
            验证是否通过
        """
        # TODO: 实现API密钥验证
        # 这里需要调用AI服务模块验证API密钥
        return True
