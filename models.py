from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """用户模型"""
    user_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    total_points: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class CheckinRecord:
    """签到记录模型"""
    id: Optional[int]
    user_id: int
    checkin_date: str  # YYYY-MM-DD格式
    points_earned: int
    created_at: Optional[datetime] = None

@dataclass
class MessageRecord:
    """发言记录模型"""
    id: Optional[int]
    user_id: int
    group_id: int
    message_date: str  # YYYY-MM-DD格式
    points_earned: int
    message_count: int = 1
    created_at: Optional[datetime] = None

@dataclass
class PointsTransaction:
    """积分交易记录模型"""
    id: Optional[int]
    user_id: int
    points_change: int  # 正数为增加，负数为减少
    transaction_type: str  # 'checkin', 'message', 'admin_adjust'
    description: str
    created_at: Optional[datetime] = None
