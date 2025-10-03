"""
测试项目的 Python 代码
基于图片中的 JavaScript 代码转换而来
"""
import sys
sys.path.insert(0, 'src')
sys.path.insert(0, 'src/augmented')
import asyncio
import os
from src.augmented.mcp_client import MCPClient
from src.augmented.Agent import Agent


async def main():
    """主测试函数"""
    agent = None
    try:
        # 获取当前目录
        current_dir = os.getcwd()
        print(f"当前目录: {current_dir}")
        
        # 创建 Fetch MCP 客户端
        fetch_mcp = MCPClient(
            name='fetch',
            command='uvx',
            args=['mcp-server-fetch']
        )
        
        # 创建文件系统 MCP 客户端 
        file_mcp = MCPClient(
            name='file',
            command='npx',
            args=['-y', '@modelcontextprotocol/server-filesystem', current_dir]
        )
        
        # 创建代理实例
        agent = Agent(
            model='openai/gpt-4o-mini',  
            mcp_clients=[fetch_mcp, file_mcp]
        )
        
        # 初始化代理
        print("正在初始化代理...")
        await agent.init()
        
        # 测试查询 (对应图片中的查询)
        response = await agent.invoke(
            "获取 https://news.ycombinator.com/ 的内容，并自动概括最新消息，"
            f"并将概括结果保存到 {current_dir}/news.md 文件中"
        )
        
        print("响应结果:")
        print(response)
        
    except asyncio.CancelledError:
        print("操作被取消")
        raise
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保资源清理
        if agent is not None:
            try:
                await agent.close()
                print("代理资源已清理")
            except Exception as e:
                print(f"清理资源时出错: {e}")
    




if __name__ == "__main__":
    # 运行主函数
    print("开始测试项目...")
    asyncio.run(main())