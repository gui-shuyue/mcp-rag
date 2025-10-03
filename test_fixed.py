"""
简化的测试文件，避免导入问题
"""
import sys
import os
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "src" / "augmented"))

# 现在进行导入
try:
    from mcp_client import MCPClient
    from Agent import Agent
    print("✅ 导入成功！")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


async def simple_test():
    """简单的功能测试"""
    print("🚀 开始简单测试...")
    
    # 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ 请设置 OPENAI_API_KEY 环境变量")
        return False
    
    print(f"✅ API Key 已设置: {'*' * 10}...{api_key[-10:]}")
    
    try:
        # 创建 MCP 客户端
        print("📡 创建 MCP 客户端...")
        fetch_mcp = MCPClient(
            name='fetch',
            command='uvx',
            args=['mcp-server-fetch']
        )
        
        # 创建代理
        print("🤖 创建代理...")
        agent = Agent(
            model='openai/gpt-4o-mini',
            mcp_clients=[fetch_mcp]
        )
        
        print("✅ 对象创建成功！")
        
        # 尝试初始化
        print("⚡ 初始化代理...")
        await agent.init()
        print("✅ 代理初始化成功！")
        
        # 简单测试查询
        print("💬 执行简单查询...")
        response = await agent.invoke("Hello! 请简单回复一下。")
        print(f"📝 响应: {response}")
        
        # 关闭连接
        await agent.close()
        print("✅ 测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🎯 MCP-RAG 项目简化测试")
    print("=" * 50)
    
    try:
        result = asyncio.run(simple_test())
        if result:
            print("\n🎉 所有测试通过！")
        else:
            print("\n❌ 测试失败")
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断测试")
    except Exception as e:
        print(f"\n💥 程序异常: {e}")