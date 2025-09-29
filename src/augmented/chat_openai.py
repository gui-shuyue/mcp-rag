import asyncio # Python 的异步编程标准库，提供异步/等待（async/await）编程支持
import os
from mcp import Tool #定义和管理 AI 模型可以使用的工具
from openai import AsyncOpenAI #与 OpenAI API 进行异步通信
from dataclasses import dataclass, field #装饰器，用于自动生成类的特殊方法
                                         #field用于自定义 dataclass 字段的行为
                                         #自动生成 __init__、__repr__ 等方法
                                         # 简化类的定义
                                         # 提供类型提示支持