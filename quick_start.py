#!/usr/bin/env python3
"""
快速启动脚本 - 使用默认配置启动机器人
"""

import os
import sys
import logging

# 设置环境变量（如果.env文件不存在）
if not os.path.exists('.env'):
    print("📝 创建默认配置文件...")
    
    # 创建.env文件
    env_content = """# Telegram Bot 配置
BOT_TOKEN=8197758331:AAFWsMFekmFDZyTQ5zKu4BI40ZZ4L86jHzs

# 群组ID配置（请替换为实际的群组ID）
CHECKIN_GROUP_ID=-1001234567890  # 签到群ID（负数）
SEARCH_GROUP_ID=-1001234567891   # 搜索群ID（负数）

# 积分配置
CHECKIN_POINTS_MIN=5             # 签到最少积分
CHECKIN_POINTS_MAX=10            # 签到最多积分
MESSAGE_POINTS=1                 # 发言获得积分
SEARCH_MESSAGE_COST=1            # 搜索群发言消耗积分
MAX_CHECKIN_PER_DAY=1           # 每日最大签到次数
MAX_MESSAGE_POINTS_PER_DAY=10   # 每日发言最大积分

# 数据库配置
DATABASE_PATH=bot_data.db

# 管理员配置（用逗号分隔多个管理员ID）
ADMIN_USER_IDS=123456789
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ 已创建 .env 配置文件")
    print("⚠️  请修改 CHECKIN_GROUP_ID 和 SEARCH_GROUP_ID 为实际的群组ID")
    print("⚠️  请修改 ADMIN_USER_IDS 为您的用户ID")
    print()

def main():
    print("🚀 Telegram 积分机器人快速启动")
    print("=" * 50)
    
    try:
        # 导入并启动机器人
        from main import main as bot_main
        bot_main()
    except KeyboardInterrupt:
        print("\n👋 机器人已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("\n💡 解决方案:")
        print("1. 检查网络连接")
        print("2. 确认BOT_TOKEN是否正确")
        print("3. 确认群组ID是否正确")
        print("4. 运行 python test_config.py 检查配置")
        sys.exit(1)

if __name__ == "__main__":
    main()
