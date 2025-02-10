#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DeepSeek AI服务实现
通过 SiliconFlow API 调用 DeepSeek 模型
"""

import json
import requests
import time
from typing import Dict, Any, Optional

from utils.logger import logger

class DeepSeekAIService:
    """DeepSeek AI服务类"""
    
    DEFAULT_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
    DEFAULT_MODEL = "Pro/deepseek-ai/DeepSeek-R1"
    DEFAULT_TIMEOUT = 60  # 默认超时时间（秒）
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 2  # 重试延迟（秒）
    
    def __init__(self, api_key: str, model: str = DEFAULT_MODEL, api_url: str = DEFAULT_API_URL, timeout: int = DEFAULT_TIMEOUT):
        """初始化DeepSeek AI服务
        
        Args:
            api_key: API密钥
            model: 模型名称，默认使用 DeepSeek-R1
            api_url: API完整URL
            timeout: 请求超时时间（秒）
        """
        # 处理 API 密钥，确保格式正确
        self.api_key = api_key.strip()
        # 如果密钥已经包含 Bearer 前缀，则移除它
        if self.api_key.lower().startswith('bearer '):
            self.api_key = self.api_key[7:].strip()
            
        self.model = model
        self.api_url = api_url
        self.timeout = timeout
        
        # 设置请求头
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, payload: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """发送API请求并处理重试逻辑
        
        Args:
            payload: 请求数据
            retry_count: 当前重试次数
            
        Returns:
            Dict[str, Any]: API响应数据
        """
        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            
            # 处理错误响应
            error_data = response.json().get("error", {})
            error_message = error_data.get("message", "未知错误")
            error_type = error_data.get("type", "")
            
            # 如果是可重试的错误且未超过最大重试次数
            if (response.status_code in [429, 500, 502, 503, 504] and 
                retry_count < self.MAX_RETRIES):
                logger.warning(f"请求失败（状态码：{response.status_code}），准备第{retry_count + 1}次重试")
                time.sleep(self.RETRY_DELAY * (retry_count + 1))  # 指数退避
                return self._make_request(payload, retry_count + 1)
            
            raise Exception(f"API请求失败: {response.status_code} - {error_message}")
            
        except requests.exceptions.Timeout:
            if retry_count < self.MAX_RETRIES:
                logger.warning(f"请求超时，准备第{retry_count + 1}次重试")
                time.sleep(self.RETRY_DELAY * (retry_count + 1))
                return self._make_request(payload, retry_count + 1)
            raise Exception("API请求多次超时，请检查网络连接或稍后重试")
            
        except requests.exceptions.ConnectionError:
            if retry_count < self.MAX_RETRIES:
                logger.warning(f"连接错误，准备第{retry_count + 1}次重试")
                time.sleep(self.RETRY_DELAY * (retry_count + 1))
                return self._make_request(payload, retry_count + 1)
            raise Exception("无法连接到API服务器，请检查网络连接")
            
        except Exception as e:
            raise Exception(f"API请求异常: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """验证API密钥是否有效
        
        Returns:
            bool: 密钥是否有效
        """
        try:
            # 准备请求数据
            payload = {
                "messages": [
                    {
                        "content": "测试连接",
                        "role": "user"
                    }
                ],
                "model": self.model
            }
            
            # 发送请求
            response = self._make_request(payload)
            return True
                
        except Exception as e:
            logger.error(f"验证API密钥时发生错误: {str(e)}")
            raise
    
    def generate_content(self, prompt: str, context: Optional[str] = None, max_tokens: int = 1000) -> Dict[str, Any]:
        """生成内容
        
        Args:
            prompt: 提示词
            context: 上下文（可选）
            max_tokens: 最大生成token数
            
        Returns:
            Dict[str, Any]: 生成的内容，包含text字段
        """
        try:
            # 准备消息列表
            messages = []
            
            # 如果有上下文，添加到消息列表
            if context:
                messages.append({
                    "content": f"Previous context: {context}",
                    "role": "system"
                })
            
            # 添加用户提示
            messages.append({
                "content": prompt,
                "role": "user"
            })
            
            # 准备请求数据
            payload = {
                "messages": messages,
                "model": self.model,
                "max_tokens": max_tokens
            }
            
            # 发送请求
            response = self._make_request(payload)
            generated_text = response["choices"][0]["message"]["content"]
            return {"text": generated_text.strip()}
                
        except Exception as e:
            error_msg = f"生成内容时发生错误: {str(e)}"
            logger.error(error_msg)
            return {"error": error_msg}
    
    def retry_on_error(self, func, max_retries: int = 3, *args, **kwargs):
        """错误重试装饰器
        
        Args:
            func: 要重试的函数
            max_retries: 最大重试次数
            *args: 函数参数
            **kwargs: 函数关键字参数
            
        Returns:
            Any: 函数返回值
        """
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if i == max_retries - 1:  # 最后一次重试
                    raise e
                logger.warning(f"第{i+1}次重试失败: {str(e)}")
                continue
