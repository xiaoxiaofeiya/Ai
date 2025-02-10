#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
提示词管理模块
管理不同场景的提示词模板
"""

from typing import Dict, Any, Optional

class PromptTemplate:
    """提示词模板类"""
    
    # 默认的内容生成提示词模板
    DEFAULT_CONTENT_GENERATION = """
你是一位专业的{genre}作家，擅长创作{style}风格的作品。
请根据以下提示创作内容：

{prompt}

要求：
1. 内容要符合{genre}的特点
2. 风格要体现{style}的特色
3. 字数在{min_words}到{max_words}之间
4. 注意文章的连贯性和逻辑性
"""

    # 默认的续写提示词模板
    DEFAULT_CONTENT_CONTINUATION = """
你是一位专业的{genre}作家，擅长创作{style}风格的作品。
请基于以下内容进行续写：

已有内容：
{context}

要求：
1. 续写内容要与前文保持一致的风格和语气
2. 确保情节/内容的连贯性
3. 续写字数在{min_words}到{max_words}之间
4. 注意承上启下的过渡自然
"""

    def __init__(self):
        """初始化提示词模板"""
        # 当前使用的模板
        self.content_generation = self.DEFAULT_CONTENT_GENERATION
        self.content_continuation = self.DEFAULT_CONTENT_CONTINUATION
    
    @classmethod
    def get_generation_prompt(cls, prompt: str, custom_template: Optional[str] = None, **kwargs) -> str:
        """获取内容生成的提示词
        
        Args:
            prompt: 用户输入的提示词
            custom_template: 用户自定义的模板（如果为None则使用默认模板）
            **kwargs: 其他参数
                - genre: 作品类型（默认为"小说"）
                - style: 写作风格（默认为"现代"）
                - min_words: 最小字数（默认为500）
                - max_words: 最大字数（默认为1000）
            
        Returns:
            格式化后的提示词
        """
        params = {
            'genre': kwargs.get('genre', '小说'),
            'style': kwargs.get('style', '现代'),
            'min_words': kwargs.get('min_words', 500),
            'max_words': kwargs.get('max_words', 1000),
            'prompt': prompt
        }
        
        # 使用自定义模板或默认模板
        template = custom_template if custom_template else cls.DEFAULT_CONTENT_GENERATION
        
        try:
            return template.format(**params)
        except KeyError as e:
            # 如果自定义模板格式化失败，回退到默认模板
            return cls.DEFAULT_CONTENT_GENERATION.format(**params)
    
    @classmethod
    def get_continuation_prompt(cls, context: str, custom_template: Optional[str] = None, **kwargs) -> str:
        """获取续写的提示词
        
        Args:
            context: 已有内容
            custom_template: 用户自定义的模板（如果为None则使用默认模板）
            **kwargs: 其他参数
                - genre: 作品类型（默认为"小说"）
                - style: 写作风格（默认为"现代"）
                - min_words: 最小字数（默认为300）
                - max_words: 最大字数（默认为800）
            
        Returns:
            格式化后的提示词
        """
        params = {
            'genre': kwargs.get('genre', '小说'),
            'style': kwargs.get('style', '现代'),
            'min_words': kwargs.get('min_words', 300),
            'max_words': kwargs.get('max_words', 800),
            'context': context
        }
        
        # 使用自定义模板或默认模板
        template = custom_template if custom_template else cls.DEFAULT_CONTENT_CONTINUATION
        
        try:
            return template.format(**params)
        except KeyError as e:
            # 如果自定义模板格式化失败，回退到默认模板
            return cls.DEFAULT_CONTENT_CONTINUATION.format(**params)
    
    @staticmethod
    def validate_template(template: str, params: Dict[str, Any]) -> bool:
        """验证模板是否有效
        
        Args:
            template: 要验证的模板
            params: 用于测试的参数
            
        Returns:
            模板是否有效
        """
        try:
            template.format(**params)
            return True
        except (KeyError, ValueError, IndexError):
            return False
