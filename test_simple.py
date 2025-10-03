"""
简单的项目测试文件
测试各个组件的基本功能
"""
import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.augmented.mcp_client import MCPClient
from src.augmented.Agent import Agent


async def test_mcp_client():
    """测试 MCP 客户端基本功能"""
    print("\n=== 测试 MCP 客户端 ===")
    
    # 创建 Fetch MCP 客户端
    fetch_mcp = MCPClient(
        name='fetch',
        command='uvx',
        args=['mcp-server-fetch']
    )
    
    try:
        print("初始化 Fetch MCP 客户端...")
        await fetch_mcp.init()
        
        # 获取工具列表
        tools = fetch_mcp.getTools()
        print(f"可用工具数量: {len(tools)}")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
            
        return fetch_mcp
        
    except Exception as e:
        print(f"MCP 客户端测试失败: {e}")
        return None


async def test_agent_basic():
    """测试代理基本功能"""
    print("\n=== 测试代理基本功能 ===")
    
    # 创建一个简单的 MCP 客户端
    fetch_mcp = MCPClient(
        name='fetch',
        command='uvx',
        args=['mcp-server-fetch']
    )
    
    # 创建代理
    agent = Agent(
        model='openai/gpt-4o-mini',
        mcp_clients=[fetch_mcp],
        system_prompt="你是一个helpful的AI助手"
    )
    
    try:
        print("初始化代理...")
        await agent.init()
        
        print("代理初始化成功！")
        return agent
        
    except Exception as e:
        print(f"代理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_simple_query():
    """测试简单查询"""
    print("\n=== 测试简单查询 ===")
    
    fetch_mcp = MCPClient(
        name='fetch',
        command='uvx',
        args=['mcp-server-fetch']
    )
    
    agent = Agent(
        model='openai/gpt-4o-mini',
        mcp_clients=[fetch_mcp]
    )
    
    try:
        await agent.init()
        
        # 简单的测试查询
        response = await agent.invoke("请说 Hello World!")
        print(f"响应: {response}")
        
        await agent.close()
        return True
        
    except Exception as e:
        print(f"查询测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主测试函数"""
    print("🚀 开始项目功能测试")
    
    # 检查环境变量
    print("\n=== 检查环境变量 ===")
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    if api_key:
        print(f"✅ OPENAI_API_KEY: {'*' * 10}...{api_key[-10:]}")
    else:
        print("❌ OPENAI_API_KEY 未设置")
    
    if base_url:
        print(f"✅ OPENAI_BASE_URL: {base_url}")
    else:
        print("❌ OPENAI_BASE_URL 未设置")
    
    # 测试 1: MCP 客户端
    mcp_client = await test_mcp_client()
    if mcp_client:
        try:
            await mcp_client.close()
        except:
            pass
    
    # 测试 2: 代理基本功能
    agent = await test_agent_basic()
    if agent:
        try:
            await agent.close()
        except:
            pass
    
    # 测试 3: 简单查询 (如果前面都成功)
    if mcp_client and agent:
        await test_simple_query()
    
    print("\n🏁 测试完成！")


if __name__ == "__main__":
    asyncio.run(main())