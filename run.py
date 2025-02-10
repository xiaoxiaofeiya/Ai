#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI写作助手程序入口
"""

import sys
from pathlib import Path

# 添加src目录到Python路径
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.main import create_application, load_stylesheet, create_main_window

def main():
    """程序入口函数"""
    # 创建应用
    app = create_application(sys.argv)
    
    # 加载样式表
    load_stylesheet(app)
    
    # 创建并显示主窗口
    window = create_main_window()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 