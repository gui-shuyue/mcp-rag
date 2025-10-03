# import asyncio
# from typing import Optional
# from contextlib import AsyncExitStack

# from mcp import ClientSession, StdioServerParameters
# from mcp.client.stdio import stdio_client

# from dotenv import load_dotenv

# load_dotenv()  # load environment variables from .env

import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool

class MCPClient:
    def __init__(
        self,
        name: str,
        command: str,
        args: list[str],
        version: str = "1.0.0"
    ):
        self.exit_stack = AsyncExitStack()
        self.session: Optional[ClientSession] = None
        self.tools: list[Tool] = []
        self.name = name
        self.command = command
        self.args = args
        self.version = version
        self._closed = False  # 添加关闭状态标记

    async def connectToServer(self):
        """连接到 MCP 服务器并获取可用工具"""
        try:
            # 创建服务器参数
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args
            )
            
            # 创建传输层
            stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = stdio_transport
            
            # 创建会话
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(stdio, write)
            )
            
            # 初始化会话
            await self.session.initialize()
            
            # 获取可用工具列表
            response = await self.session.list_tools()
            self.tools = response.tools
            
            print(f"Connected to server with tools: {[tool.name for tool in self.tools]}")
            
        except Exception as e:
            print(f"Failed to connect to MCP server: {e}")
            raise e

    async def close(self):
        """关闭 MCP 客户端连接"""
        if not self._closed:
            try:
                # 尝试安全关闭
                await asyncio.wait_for(self.exit_stack.aclose(), timeout=2.0)
                self._closed = True
                print(f"Successfully closed MCP client {self.name}")
            except asyncio.TimeoutError:
                print(f"Warning: Timeout closing MCP client {self.name}, marking as closed")
                self._closed = True
            except RuntimeError as e:
                if "cancel scope" in str(e):
                    # 这是已知的 anyio 问题，安全忽略
                    print(f"Warning: Known anyio issue when closing MCP client {self.name}: {e}")
                    self._closed = True
                else:
                    print(f"Warning: Runtime error closing MCP client {self.name}: {e}")
                    self._closed = True
            except Exception as e:
                print(f"Warning: Unexpected error closing MCP client {self.name}: {e}")
                self._closed = True

    async def init(self):
        """初始化 MCP 客户端"""
        await self.connectToServer()

    def getTools(self) -> list[Tool]:
        """获取可用工具列表
        
        Returns:
            list[Tool]: 工具列表
        """
        return self.tools

    async def call_tool(self, tool_name: str, params: dict):
        return await self.session.call_tool(tool_name, params)
             


       

async def example():
    """测试 MCPClient 的基本功能"""
    fetchMcp = None
    try:
        # 创建 fetch 服务的客户端实例
        fetchMcp = MCPClient(
            name='fetch',
            command='uvx',
            args=['mcp-server-fetch']
        )
        
        # 初始化客户端
        print("正在初始化客户端...")
        await fetchMcp.init()
        
        # 获取工具列表
        tools = fetchMcp.getTools()
        print("\n可用工具列表:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
    finally:
        # 确保资源被正确清理
        if fetchMcp:
            try:
                await fetchMcp.close()
                print("\n客户端已关闭")
            except Exception as e:
                print(f"关闭客户端时出错: {e}")

if __name__ == "__main__":
    asyncio.run(example())
#         """Connect to an MCP server

#         Args:
#             server_script_path: Path to the server script (.py or .js)
#         """
#         is_python = server_script_path.endswith('.py')
#         is_js = server_script_path.endswith('.js')
#         if not (is_python or is_js):
#             raise ValueError("Server script must be a .py or .js file")

#         command = "python" if is_python else "node"
#         server_params = StdioServerParameters(
#             command=command,
#             args=[server_script_path],
#             env=None
#         )

#         stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
#         self.stdio, self.write = stdio_transport
#         self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

#         await self.session.initialize()

#         # List available tools
#         response = await self.session.list_tools()
#         tools = response.tools
#         print("\nConnected to server with tools:", [tool.name for tool in tools])


#     async def process_query(self, query: str) -> str:
#         """Process a query using Claude and available tools"""
#         messages = [
#             {
#                 "role": "user",
#                 "content": query
#             }
#         ]

#         response = await self.session.list_tools()
#         available_tools = [{
#             "name": tool.name,
#             "description": tool.description,
#             "input_schema": tool.inputSchema
#         } for tool in response.tools]

#         # Initial Claude API call
#         response = self.anthropic.messages.create(
#             model="claude-3-5-sonnet-20241022",
#             max_tokens=1000,
#             messages=messages,
#             tools=available_tools
#         )

#         # Process response and handle tool calls
#         final_text = []

#         assistant_message_content = []
#         for content in response.content:
#             if content.type == 'text':
#                 final_text.append(content.text)
#                 assistant_message_content.append(content)
#             elif content.type == 'tool_use':
#                 tool_name = content.name
#                 tool_args = content.input

#                 # Execute tool call
#                 result = await self.session.call_tool(tool_name, tool_args)
#                 final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

#                 assistant_message_content.append(content)
#                 messages.append({
#                     "role": "assistant",
#                     "content": assistant_message_content
#                 })
#                 messages.append({
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "tool_result",
#                             "tool_use_id": content.id,
#                             "content": result.content
#                         }
#                     ]
#                 })

#                 # Get next response from Claude
#                 response = self.anthropic.messages.create(
#                     model="claude-3-5-sonnet-20241022",
#                     max_tokens=1000,
#                     messages=messages,
#                     tools=available_tools
#                 )

#                 final_text.append(response.content[0].text)

#         return "\n".join(final_text)
    
#     async def chat_loop(self):
#         """Run an interactive chat loop"""
#         print("\nMCP Client Started!")
#         print("Type your queries or 'quit' to exit.")

#         while True:
#             try:
#                 query = input("\nQuery: ").strip()

#                 if query.lower() == 'quit':
#                     break

#                 response = await self.process_query(query)
#                 print("\n" + response)

#             except Exception as e:
#                 print(f"\nError: {str(e)}")

#     async def cleanup(self):
#         """Clean up resources"""
#         await self.exit_stack.aclose()


# async def main():
#     if len(sys.argv) < 2:
#         print("Usage: python client.py <path_to_server_script>")
#         sys.exit(1)

#     client = MCPClient()
#     try:
#         await client.connect_to_server(sys.argv[1])
#         await client.chat_loop()
#     finally:
#         await client.cleanup()

# if __name__ == "__main__":
#     import sys
#     asyncio.run(main())

# import asyncio
# import shlex
# from typing import Optional
# from contextlib import AsyncExitStack

# from mcp import ClientSession, StdioServerParameters, Tool
# from mcp.client.stdio import stdio_client

# from rich import print as rprint

# from dotenv import load_dotenv

# from utils.info import PROJECT_ROOT_DIR
# from utils.pretty import log_title

# load_dotenv()


# class MCPClient:
#     def __init__(
#         self,
#         name: str,
#         command: str,
#         args: list[str],
#         version: str = "0.0.1",
#     ):
#         self.session: Optional[ClientSession] = None
#         self.exit_stack = AsyncExitStack()
#         self.name = name
#         self.version = version
#         self.command = command
#         self.args = args
#         self.tools: list[Tool] = []

#     async def init(self):
#         await self._connect_to_server()

#     async def close(self):
#         await self.exit_stack.aclose()

#     def get_tools(self):
#         return self.tools

#     async def _connect_to_server(
#         self,
#     ):
#         """
#         Connect to an MCP server
#         """
#         server_params = StdioServerParameters(
#             command=self.command,
#             args=self.args,
#         )

#         stdio_transport = await self.exit_stack.enter_async_context(
#             stdio_client(server_params),
#         )
#         self.stdio, self.write = stdio_transport
#         self.session = await self.exit_stack.enter_async_context(
#             ClientSession(self.stdio, self.write)
#         )

#         await self.session.initialize()

#         # List available tools
#         response = await self.session.list_tools()
#         self.tools = response.tools
#         rprint("\nConnected to server with tools:", [tool.name for tool in self.tools])


# async def example():
#     for mcp_name, cmd in [
#         (
#             "filesystem",
#             f"npx -y @modelcontextprotocol/server-filesystem {PROJECT_ROOT_DIR!s}",
#         ),
#         (
#             "fetch",
#             "uvx mcp-server-fetch",
#         ),
#     ]:
#         log_title(mcp_name)
#         command, *args = shlex.split(cmd)
#         mcp_client = MCPClient(
#             name=mcp_name,
#             command=command,
#             args=args,
#         )
#         await mcp_client.init()
#         tools = mcp_client.get_tools()
#         rprint(tools)
#         await mcp_client.close()


# if __name__ == "__main__":
#     asyncio.run(example())