import asyncio # Python 的异步编程标准库，提供异步/等待（async/await）编程支持
import os
from mcp import Tool #定义和管理 AI 模型可以使用的工具
from openai import AsyncOpenAI #与 OpenAI API 进行异步通信
from dataclasses import dataclass, field #装饰器，用于自动生成类的特殊方法
                                         #field用于自定义 dataclass 字段的行为
                                         #自动生成 __init__、__repr__ 等方法
                                         # 简化类的定义
                                         # 提供类型提示支持
from openai.types import FunctionDefinition #定义与 OpenAI API 交互时使用的函数
from openai.types.chat import(
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
)
import dotenv
from pydantic import BaseModel #TODO
from rich import print as rprint

from utils import pretty

dotenv.load_dotenv() #加载环境变量，从 .env 文件中读取配置

class ToolCallFunction(BaseModel):
    name: str = ""
    arguments: str = ""

class ToolCall(BaseModel):
    id: str = ""
    function: ToolCallFunction = ToolCallFunction()

class ChatOpenAIChatResponse(BaseModel):
    content: str = ""
    tool_calls: list[ToolCall] = []


@dataclass
class AsyncChatOpenAI:
    model: str
    messages:list[ChatCompletionMessageParam] = field(default_factory=list) #database中的可变参数，用feild使其独立于一个实例
    tools: list[Tool] = field(default_factory=list)

    system_prompt: str = ""
    context: str = ""

    llm: AsyncOpenAI = field(init=False)
    # 该字段不会在 dataclass 的自动生成的 __init__ 方法中初始化。

    def __post_init__(self):
        self.llm = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE_URL"),
        )
        if self.system_prompt:
            self.messages.insert(0, {"role": "system", "content": self.system_prompt})
        if self.context:
            self.messages.append({"role": "user", "content": self.context})

    async def chat(self, prompt: str = "", print_llm_output: bool = True):
        pretty.log_title("CHAT")
        if prompt:
            self.messages.append({"role": "user", "content": prompt})       
            streaming = await self.llm.chat.completions.create(             
                model=self.model,
                messages=self.messages,
                tools=self.getToolsDefinitions(),
                stream=True,
            )
# # 典型 chunk 示例
# {
#     "id": "chatcmpl-...",
#     "object": "chat.completion.chunk",
#     "created": 1234567890,
#     "model": "gpt-4",
#     "choices": [
#         {
#             "index": 0,
#             "delta": {
#                 "content": "Hello",  # 部分内容
#                 "tool_calls": [...]   # 工具调用（可选）
#             },
#             "finish_reason": None
#         }
#     ]
# }

        pretty.log_title("RESPONSE")
        content = ""
        tool_calls: list[ToolCall] = []
        printed_llm_output = False
        async for chunk in streaming:
            delta = chunk.choices[0].delta
            if delta.content:
                content += delta.content
                if print_llm_output:
                   print(delta.content, end="")
                   printed_llm_output = True
            
            if delta.tool_calls:
                for tool_call_chunk in delta.tool_calls:
                    if len(tool_calls) <= tool_call_chunk.index:
                        tool_calls.append(ToolCall())
                    current_call = tool_calls[tool_call_chunk.index]
                    if tool_call_chunk.id:
                        current_call.id = tool_call_chunk.id or ""
                    if tool_call_chunk.function:
                        current_call.function.name = tool_call_chunk.function.name or ""
                        current_call.function.arguments = (tool_call_chunk.function.arguments or "")
# # 典型 tool_call_chunk
# {
#     "index": 0,
#     "id": "call_123",
#     "function": {
#         "name": "get_weather",
#         "arguments": '{"city": "北京"}'
#     }
# }
            
        
            if printed_llm_output:
                print()
            self.messages.append(
                {
                    "role": "assistant", 
                    "content": content,
                    "tool_calls": [
                        {
                            "type": "function",
                            "id": tool.id,
                            "function": {
                                "name": tool.function.name,
                                "arguments": tool.function.arguments,
                            } ,
                        }
                        for tool in tool_calls
                    ]
                }
            )
            return ChatOpenAIChatResponse(
                content=content,
                tool_calls=tool_calls,
            )
    
    
    
    
    def getToolsDefinitions(self) -> list[ChatCompletionToolParam]:
        return [
            ChatCompletionToolParam(
                type = "function",
                parameters=FunctionDefinition(
                    name=tool.name,
                    description=tool.description,
                    parameters=tool.inputSchema,
                ),
            )
            for tool in self.tools
        ]
    # ChatCompletionToolParam:
    # {
    # "type": "function",  # 工具类型，目前仅支持 "function"
    # "function": {
    #     "name": str,        # 函数名称
    #     "description": str, # 函数描述
    #     "parameters": dict  # 参数定义（JSON Schema）
    # }
    # }

async def example():
    llm = AsyncChatOpenAI(
        model="gpt-4o-mini",
    )
    chat_resp = await llm.chat(prompt="Hello")
    rprint(chat_resp)


if __name__ == "__main__":
    asyncio.run(example())