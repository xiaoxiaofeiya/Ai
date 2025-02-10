"""
AI写作助手
一个基于AI的智能写作辅助工具
"""

__version__ = '1.0.0'

from .main import create_application, load_stylesheet, create_main_window

__all__ = [
    'create_application',
    'load_stylesheet',
    'create_main_window',
    '__version__'
] 