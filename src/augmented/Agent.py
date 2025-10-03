from typing import Optional
from utils import pretty
from chat_openai import AsyncChatOpenAI
from mcp_client import MCPClient
import json
from rich import print as rprint


class Agent:
    def __init__(self, model: str, mcp_clients: list[MCPClient], system_prompt: str = "", context: str = ""):
        self.mcp_clients = mcp_clients
        self.llm: AsyncChatOpenAI | None = None  
        self.model: str = model
        self.system_prompt: str = system_prompt
        self.context: str = context
    
    async def init(self):
        pretty.log_title("INIT LLM AND TOOLS")
        tools = []
        
        # 初始化所有 MCP 客户端
        for mcp_client in self.mcp_clients:
            await mcp_client.init()
            tools.extend(mcp_client.getTools())
        
        self.llm = AsyncChatOpenAI(
            model=self.model,
            tools=tools,
            system_prompt=self.system_prompt,
            context=self.context,
        )
        
    async def close(self):
        pretty.log_title("CLOSE MCP CLIENTS")
        for mcp_client in self.mcp_clients:
            try:
                await mcp_client.close()
            except Exception as e:
                print(f"Warning: Error closing MCP client {mcp_client.name}: {e}")

    async def invoke(self, prompt: str) -> str | None:
        # 移除自动关闭逻辑，让调用者控制生命周期
        return await self._invoke(prompt)

    async def _invoke(self, prompt: str) -> str | None:
        if self.llm is None:
            raise ValueError("llm not call .init()")
        chat_resp = await self.llm.chat(prompt)
        i = 0
        while True:
            pretty.log_title(f"INVOKE CYCLE {i}")
            i += 1
            # 处理工具调用
            rprint(chat_resp)
            if chat_resp.tool_calls:
                for tool_call in chat_resp.tool_calls:
                    target_mcp_client: MCPClient | None = None
                    for mcp_client in self.mcp_clients:
                        if tool_call.function.name in [
                            t.name for t in mcp_client.getTools()
                        ]:
                            target_mcp_client = mcp_client
                            break
                    if target_mcp_client:
                        pretty.log_title(f"TOOL USE `{tool_call.function.name}`")
                        rprint("with args:", tool_call.function.arguments)
                        mcp_result = await target_mcp_client.call_tool(
                            tool_call.function.name,
                            json.loads(tool_call.function.arguments),
                        )
                        rprint("call result:", mcp_result)
                        self.llm.append_tool_result(
                            tool_call.id, mcp_result.model_dump_json()
                        )
                    else:
                        self.llm.append_tool_result(tool_call.id, "tool not found")
                chat_resp = await self.llm.chat()
            else:
                return chat_resp.content
