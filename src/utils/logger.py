#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
日志模块
提供统一的日志记录功能
"""

import sys
from pathlib import Path
from loguru import logger

def setup_logger():
    """配置日志记录器"""
    # 创建日志目录
    log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 设置日志文件路径
    log_file = log_dir / "app.log"
    
    # 配置日志格式
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    # 移除默认的处理器
    logger.remove()
    
    # 添加控制台输出
    logger.add(
        sys.stderr,
        format=log_format,
        level="INFO",
        colorize=True
    )
    
    # 添加文件输出
    logger.add(
        str(log_file),
        format=log_format,
        level="DEBUG",
        rotation="10 MB",  # 当日志文件达到10MB时轮换
        retention="1 month",  # 保留1个月的日志
        compression="zip",  # 压缩旧的日志文件
        encoding="utf-8"
    )
    
    logger.info("日志系统初始化完成")
    
    return logger
