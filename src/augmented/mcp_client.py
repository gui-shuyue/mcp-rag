import asyncio
import shlex

from typing import Any, Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters, Tool
from mcp.client.stdio import stdio_client

from rich import print as rprint

from dotenv import load_dotenv

from utils.info import PROJECT_ROOT_DIR
from utils.pretty import log_title

load_dotenv()


class MCPClient:
    def __init__(
        self,
        name: str,
        command: str,
        args: list[str],
        version: str = "0.0.1",
    ):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.name = name
        self.version = version
        self.command = command
        self.args = args
        self.tools: list[Tool] = []

    async def init(self):
        await self._connect_to_server()

    async def close(self):
        try:
            await self.exit_stack.aclose()
        except Exception as e:
            print(f"Warning: Error closing MCP client {self.name}: {e}")

    def getTools(self):
        return self.tools

    async def _connect_to_server(
        self,
    ):
        """
        Connect to an MCP server
        """
        server_params = StdioServerParameters(
            command=self.command,
            args=self.args,
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params),
        )
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        self.tools = response.tools
        rprint("\nConnected to server with tools:", [tool.name for tool in self.tools])

    async def call_tool(self, name: str, params: dict[str, Any]):
        return await self.session.call_tool(name, params)