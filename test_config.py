#!/usr/bin/env python3
"""
配置测试脚本
用于验证机器人配置是否正确
"""

import os
import sys
from dotenv import load_dotenv

def test_config():
    """测试配置"""
    print("🧪 测试机器人配置")
    print("=" * 40)
    
    # 加载环境变量
    if not os.path.exists('.env'):
        print("❌ 未找到 .env 文件")
        return False
    
    load_dotenv()
    
    # 测试配置项
    configs = {
        'BOT_TOKEN': os.getenv('BOT_TOKEN'),
        'CHECKIN_GROUP_ID': os.getenv('CHECKIN_GROUP_ID'),
        'SEARCH_GROUP_ID': os.getenv('SEARCH_GROUP_ID'),
        'CHECKIN_POINTS_MIN': os.getenv('CHECKIN_POINTS_MIN', '5'),
        'CHECKIN_POINTS_MAX': os.getenv('CHECKIN_POINTS_MAX', '10'),
        'MESSAGE_POINTS': os.getenv('MESSAGE_POINTS', '1'),
        'SEARCH_MESSAGE_COST': os.getenv('SEARCH_MESSAGE_COST', '1'),
        'ADMIN_USER_IDS': os.getenv('ADMIN_USER_IDS', ''),
    }
    
    print("📋 配置信息:")
    for key, value in configs.items():
        if key == 'BOT_TOKEN':
            # 隐藏token的大部分内容
            display_value = f"{value[:10]}...{value[-10:]}" if value else "未设置"
        else:
            display_value = value or "未设置"
        
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {display_value}")
    
    # 检查必要配置
    required = ['BOT_TOKEN', 'CHECKIN_GROUP_ID', 'SEARCH_GROUP_ID']
    missing = [k for k in required if not configs[k]]
    
    if missing:
        print(f"\n❌ 缺少必要配置: {', '.join(missing)}")
        return False
    
    print("\n✅ 配置检查通过")
    return True

def test_database():
    """测试数据库"""
    print("\n🗄️ 测试数据库连接")
    print("-" * 40)
    
    try:
        from database import Database
        db = Database()
        print("✅ 数据库初始化成功")
        
        # 测试基本操作
        test_user = db.get_or_create_user(12345, "test_user", "Test", "User")
        print(f"✅ 用户操作测试成功: {test_user.user_id}")
        
        return True
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False

def test_telegram_connection():
    """测试Telegram连接"""
    print("\n📡 测试Telegram连接")
    print("-" * 40)
    
    try:
        import asyncio
        from telegram import Bot
        
        bot_token = os.getenv('BOT_TOKEN')
        if not bot_token:
            print("❌ 未设置BOT_TOKEN")
            return False
        
        async def test_bot():
            bot = Bot(token=bot_token)
            try:
                me = await bot.get_me()
                print(f"✅ 机器人连接成功: @{me.username}")
                return True
            except Exception as e:
                print(f"❌ 机器人连接失败: {e}")
                return False
            finally:
                await bot.close()
        
        return asyncio.run(test_bot())
        
    except Exception as e:
        print(f"❌ Telegram连接测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🔧 Telegram 积分机器人配置测试")
    print("=" * 50)
    
    success = True
    
    # 测试配置
    if not test_config():
        success = False
    
    # 测试数据库
    if not test_database():
        success = False
    
    # 测试Telegram连接
    if not test_telegram_connection():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 所有测试通过！机器人可以正常启动")
        print("💡 使用 python main.py 或 python start.py 启动机器人")
    else:
        print("❌ 测试失败，请检查配置")
        print("💡 参考 README.md 进行配置")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
