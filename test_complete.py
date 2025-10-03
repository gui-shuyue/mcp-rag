"""
完整的项目测试文件
复现图片中 JavaScript 代码的功能
"""
import asyncio
import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.augmented.mcp_client import MCPClient
from src.augmented.Agent import Agent


async def main():
    """
    主函数，复现图片中的 JavaScript 逻辑
    对应原代码：
    - 创建 fetchMCP 和 fileMCP 客户端
    - 创建 agent 代理
    - 执行网页抓取和文件保存任务
    """
    
    print("🚀 启动项目测试 (基于图片代码)")
    
    # 获取当前目录 (对应 process.cwd())
    current_dir = os.getcwd()
    print(f"📁 当前工作目录: {current_dir}")
    
    # 创建 MCP 客户端实例
    print("\n📡 创建 MCP 客户端...")
    
    # Fetch MCP 客户端 (对应 fetchMCP)
    fetch_mcp = MCPClient(
        name='fetch',
        command='uvx', 
        args=['mcp-server-fetch']
    )
    
    # 文件系统 MCP 客户端 (对应 fileMCP)
    file_mcp = MCPClient(
        name='file',
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem', current_dir]
    )
    
    # 创建代理 (对应 agent)
    print("\n🤖 创建 AI 代理...")
    agent = Agent(
        model='openai/gpt-4o-mini',  # 对应图片中的模型
        mcp_clients=[fetch_mcp, file_mcp]
    )
    
    try:
        # 初始化代理 (对应 await agent.init())
        print("⚡ 初始化代理中...")
        await agent.init()
        print("✅ 代理初始化成功!")
        
        # 执行任务 (对应 await agent.invoke())
        print("\n🌐 开始执行网页抓取和文件保存任务...")
        
        query = """
        获取 https://news.ycombinator.com/ 的内容，
        并自动概括最新的新闻消息，
        然后将概括结果保存到当前目录下的 news.md 文件中。
        """
        
        print(f"📝 执行查询: {query.strip()}")
        
        # 调用代理执行任务
        response = await agent.invoke(query)
        
        # 输出结果 (对应 console.log(response))
        print("\n📋 任务执行结果:")
        print("=" * 50)
        print(response)
        print("=" * 50)
        
        # 检查文件是否创建成功
        news_file = os.path.join(current_dir, 'news.md')
        if os.path.exists(news_file):
            print(f"\n✅ 文件已成功创建: {news_file}")
            # 显示文件大小
            file_size = os.path.getsize(news_file)
            print(f"📄 文件大小: {file_size} 字节")
        else:
            print(f"\n❌ 文件未找到: {news_file}")
            
    except Exception as e:
        print(f"\n❌ 执行过程中出现错误:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 显示详细的错误堆栈
        import traceback
        print("\n📋 详细错误信息:")
        traceback.print_exc()
        
    finally:
        # 清理资源
        print(f"\n🧹 清理资源中...")
        try:
            await agent.close()
            print("✅ 代理连接已关闭")
        except Exception as e:
            print(f"⚠️ 关闭代理时出现问题: {e}")
    
    print("\n🏁 测试完成!")


# 添加一个辅助函数来检查依赖
def check_dependencies():
    """检查必要的依赖和环境"""
    print("🔍 检查环境依赖...")
    
    # 检查环境变量
    api_key = os.getenv('OPENAI_API_KEY')
    base_url = os.getenv('OPENAI_BASE_URL')
    
    if not api_key:
        print("❌ 缺少 OPENAI_API_KEY 环境变量")
        return False
    
    if not base_url:
        print("❌ 缺少 OPENAI_BASE_URL 环境变量") 
        return False
        
    print("✅ 环境变量检查通过")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("🎯 MCP-RAG 项目完整测试")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 环境检查失败，请检查 .env 文件中的配置")
        sys.exit(1)
    
    # 运行主测试
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了测试")
    except Exception as e:
        print(f"\n\n💥 程序异常退出: {e}")
        import traceback
        traceback.print_exc()