#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI写作助手主程序逻辑
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# 在 macOS 上抑制 TSM 警告
if sys.platform == 'darwin':
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    # 重定向标准错误输出到 /dev/null 来抑制 TSM 警告
    import contextlib
    with contextlib.redirect_stderr(open(os.devnull, 'w')):
        from PyQt6.QtGui import QGuiApplication

from gui.main_window import MainWindow
from utils.logger import setup_logger

def create_application(argv):
    """创建并配置应用程序"""
    # 设置日志
    setup_logger()
    
    # 创建应用
    app = QApplication(argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    return app

def load_stylesheet(app):
    """加载样式表"""
    # 加载样式表
    style_file = Path(__file__).parent / "gui" / "themes" / "light.qss"
    if style_file.exists():
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                style_content = f.read()
                app.setStyleSheet(style_content)
        except Exception as e:
            print(f"加载样式表时出错: {e}")
    else:
        print(f"样式表文件不存在: {style_file}")

def create_main_window():
    """创建主窗口"""
    return MainWindow()

def main():
    """主程序入口函数"""
    # 创建应用
    app = create_application(sys.argv)
    
    # 加载样式表
    load_stylesheet(app)
    
    # 创建主窗口
    window = create_main_window()
    window.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 