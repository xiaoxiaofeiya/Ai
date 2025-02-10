#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI服务模块
提供AI内容生成和续写功能
"""

from .base import BaseAIService
from .deepseek import DeepSeekAIService
from .prompt import PromptTemplate

__all__ = ['BaseAIService', 'DeepSeekAIService', 'PromptTemplate'] 