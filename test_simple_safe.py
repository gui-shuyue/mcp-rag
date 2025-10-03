"""
简化的测试文件，避免异步资源管理冲突
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


async def simple_test():
    """简化的测试，避免复杂的异步资源管理"""
    print("🚀 开始简化测试...")
    
    # 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return False
    
    print(f"✅ API Key 已设置")
    
    agent = None
    try:
        # 创建 MCP 客户端
        print("📡 创建单个 MCP 客户端...")
        fetch_mcp = MCPClient(
            name='fetch',
            command='uvx',
            args=['mcp-server-fetch']
        )
        
        # 创建代理（只使用一个客户端）
        print("🤖 创建代理...")
        agent = Agent(
            model='openai/gpt-4o-mini',
            mcp_clients=[fetch_mcp],
            system_prompt="你是一个有用的AI助手。"
        )
        
        # 初始化
        print("⚡ 初始化代理...")
        await agent.init()
        print("✅ 代理初始化成功！")
        
        # 简单查询（不使用工具）
        print("💬 执行简单查询...")
        response = await agent.invoke("请简单回复：Hello World")
        print(f"📝 响应: {response}")
        
        print("✅ 测试成功完成！")
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
    print("=" * 50)
    print("🎯 MCP-RAG 项目简化测试")
    print("=" * 50)
    
    try:
        result = asyncio.run(simple_test())
        if result:
            print("\n🎉 测试通过！")
        else:
            print("\n❌ 测试失败")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n💥 程序异常: {e}")
        import traceback
        traceback.print_exc()