import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    # Telegram Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN', '8197758331:AAFWsMFekmFDZyTQ5zKu4BI40ZZ4L86jHzs')
    
    # 群组ID配置
    CHECKIN_GROUP_ID = int(os.getenv('CHECKIN_GROUP_ID', 0))  # 签到群ID
    SEARCH_GROUP_ID = int(os.getenv('SEARCH_GROUP_ID', 0))  # 搜索群ID
    
    # 积分配置
    CHECKIN_POINTS_MIN = int(os.getenv('CHECKIN_POINTS_MIN', 5))  # 签到最少积分
    CHECKIN_POINTS_MAX = int(os.getenv('CHECKIN_POINTS_MAX', 10))  # 签到最多积分
    MESSAGE_POINTS = int(os.getenv('MESSAGE_POINTS', 1))   # 发言获得积分
    SEARCH_MESSAGE_COST = int(os.getenv('SEARCH_MESSAGE_COST', 1))  # 搜索群发言消耗积分
    POINTS_EXPIRE_DAYS = int(os.getenv('POINTS_EXPIRE_DAYS', 0))  # 积分过期天数，0为永不过期
    ZERO_POINTS_COOLDOWN_HOURS = int(os.getenv('ZERO_POINTS_COOLDOWN_HOURS', 1))  # 积分为0时发言冷却时间（小时）
    BAN_DURATION_HOURS = int(os.getenv('BAN_DURATION_HOURS', 1))  # 积分不足时禁言时长（小时）

    # 签到配置
    MAX_CHECKIN_PER_DAY = int(os.getenv('MAX_CHECKIN_PER_DAY', 1))  # 每日最大签到次数
    MAX_MESSAGE_POINTS_PER_DAY = int(os.getenv('MAX_MESSAGE_POINTS_PER_DAY', 10))  # 每日发言最大积分
    
    # 数据库配置
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_data.db')
    
    # 管理员配置
    ADMIN_USER_IDS = [int(x) for x in os.getenv('ADMIN_USER_IDS', '').split(',') if x.strip()]
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN 未设置")
        if not cls.CHECKIN_GROUP_ID:
            raise ValueError("CHECKIN_GROUP_ID 未设置")
        if not cls.SEARCH_GROUP_ID:
            raise ValueError("SEARCH_GROUP_ID 未设置")
        return True

    @classmethod
    def update_config(cls, key: str, value: int):
        """动态更新配置"""
        config_map = {
            'checkin_min': 'CHECKIN_POINTS_MIN',
            'checkin_max': 'CHECKIN_POINTS_MAX',
            'message_points': 'MESSAGE_POINTS',
            'search_cost': 'SEARCH_MESSAGE_COST',
            'max_daily_points': 'MAX_MESSAGE_POINTS_PER_DAY',
            'expire_days': 'POINTS_EXPIRE_DAYS',
            'cooldown_hours': 'ZERO_POINTS_COOLDOWN_HOURS'
        }

        if key in config_map:
            attr_name = config_map[key]
            setattr(cls, attr_name, value)
            return True
        return False

    @classmethod
    def get_config_info(cls):
        """获取当前配置信息"""
        return {
            'checkin_min': cls.CHECKIN_POINTS_MIN,
            'checkin_max': cls.CHECKIN_POINTS_MAX,
            'message_points': cls.MESSAGE_POINTS,
            'search_cost': cls.SEARCH_MESSAGE_COST,
            'max_daily_points': cls.MAX_MESSAGE_POINTS_PER_DAY,
            'expire_days': cls.POINTS_EXPIRE_DAYS,
            'cooldown_hours': cls.ZERO_POINTS_COOLDOWN_HOURS
        }
