#!/usr/bin/env python3
"""
Telegram 积分机器人启动脚本
提供更友好的启动体验和错误处理
"""

import os
import sys
import logging
from pathlib import Path

def check_environment():
    """检查环境配置"""
    print("🔍 检查环境配置...")
    
    # 检查.env文件
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        print("💡 请复制 .env.example 为 .env 并填写配置")
        print("   cp .env.example .env")
        return False
    
    # 检查必要的环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['BOT_TOKEN', 'CHECKIN_GROUP_ID', 'SEARCH_GROUP_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("💡 请在 .env 文件中设置这些变量")
        return False
    
    print("✅ 环境配置检查通过")
    return True

def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    
    try:
        import telegram
        import dotenv
        print("✅ 依赖包检查通过")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖包: {e}")
        print("💡 请运行: pip install -r requirements.txt")
        return False

def main():
    """主函数"""
    print("🤖 Telegram 积分机器人启动器")
    print("=" * 40)
    
    # 检查环境
    if not check_environment():
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    print("🚀 启动机器人...")
    print("=" * 40)
    
    # 启动机器人
    try:
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 机器人运行出错: {e}")
        logging.exception("机器人运行异常")
        sys.exit(1)

if __name__ == "__main__":
    main()
