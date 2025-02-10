#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI服务基础接口
定义所有AI服务需要实现的方法
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class BaseAIService(ABC):
    """AI服务基础接口类"""
    
    @abstractmethod
    def __init__(self, api_key: str, **kwargs):
        """初始化AI服务
        
        Args:
            api_key: API密钥
            **kwargs: 其他配置参数
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效
        
        Returns:
            验证是否通过
        """
        pass
    
    @abstractmethod
    def generate_content(self, prompt: str, **kwargs) -> Optional[str]:
        """生成内容
        
        Args:
            prompt: 生成提示词
            **kwargs: 其他参数
            
        Returns:
            生成的内容或None（如果生成失败）
        """
        pass
    
    @abstractmethod
    def continue_writing(self, context: str, **kwargs) -> Optional[str]:
        """续写内容
        
        Args:
            context: 上下文内容
            **kwargs: 其他参数
            
        Returns:
            生成的内容或None（如果生成失败）
        """
        pass 