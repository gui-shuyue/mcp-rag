"""
测试工具调用功能
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "augmented"))

from mcp_client import MCPClient
from Agent import Agent


async def test_tool_usage():
    """测试工具调用功能"""
    print("🚀 开始工具调用测试...")
    
    agent = None
    try:
        # 创建 fetch MCP 客户端
        fetch_mcp = MCPClient(
            name='fetch',
            command='uvx',
            args=['mcp-server-fetch']
        )
        
        # 创建代理
        agent = Agent(
            model='openai/gpt-4o-mini',
            mcp_clients=[fetch_mcp],
            system_prompt="你是一个有用的AI助手，可以获取网页内容并进行总结。"
        )
        
        # 初始化
        print("⚡ 初始化代理...")
        await agent.init()
        print("✅ 代理初始化成功！")
        
        # 测试工具调用
        print("🌐 测试网页抓取功能...")
        response = await agent.invoke(
            "请获取 https://httpbin.org/json 的内容，并告诉我返回了什么数据"
        )
        print(f"📝 响应: {response}")
        
        print("✅ 工具调用测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 安全清理
        if agent:
            print("🧹 清理资源...")
            try:
                await agent.close()
                print("✅ 资源清理完成")
            except Exception as e:
                print(f"⚠️ 清理时出现问题（可以忽略）: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 MCP-RAG 工具调用测试")
    print("=" * 60)
    
    # 检查环境变量
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        sys.exit(1)
    
    try:
        result = asyncio.run(test_tool_usage())
        if result:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 测试失败")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        import traceback
        traceback.print_exc()