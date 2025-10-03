from typing import Optional
from utils import pretty
from chat_openai import AsyncChatOpenAI
from mcp_client import MCPClient
import json


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

    async def invoke(self, prompt:str):
        if not self.llm:
            raise ValueError("LLM not initialized. Call init() first.")
        
        response = await self.llm.chat(prompt=prompt, print_llm_output=True)
        while True:
            if len(response.tool_calls) > 0:
                for tool_call in response.tool_calls:
                    target_mcp_client: Optional[MCPClient] = None
                    for mcp_client in self.mcp_clients:
                        if tool_call.function.name in [tool.name for tool in mcp_client.getTools()]:       
                            target_mcp_client = mcp_client
                            break
                    if target_mcp_client:
                        pretty.log_title(f"TOOL USE '{tool_call.function.name}'")
                        print("with arguments:", tool_call.function.arguments)
                        mcp_result = await target_mcp_client.call_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
                        print("\nTOOL RESULT:", mcp_result)
                        self.llm.append_tool_result(tool_call.id, mcp_result.model_dump_json())
                    else:
                        self.llm.append_tool_result(tool_call.id, "tool not found")
                response = await self.llm.chat()
            else:
                # 没有工具调用，退出循环
                break
        
        return response.content
