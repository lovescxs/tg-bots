import sqlite3
import logging
from datetime import datetime, date, timedelta
from typing import Optional, List
from models import User, CheckinRecord, MessageRecord, PointsTransaction
from config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_PATH
        self.init_database()
    
    def get_connection(self):
        """获取数据库连接"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    total_points INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 签到记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS checkin_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    checkin_date TEXT,
                    points_earned INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, checkin_date)
                )
            ''')
            
            # 发言记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS message_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    message_date TEXT,
                    points_earned INTEGER,
                    message_count INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    UNIQUE(user_id, group_id, message_date)
                )
            ''')
            
            # 积分交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS points_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    points_change INTEGER,
                    transaction_type TEXT,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("数据库初始化完成")
    
    def get_or_create_user(self, user_id: int, username: str = None, 
                          first_name: str = None, last_name: str = None) -> User:
        """获取或创建用户"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 尝试获取用户
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = cursor.fetchone()
            
            if row:
                # 更新用户信息
                cursor.execute('''
                    UPDATE users SET username = ?, first_name = ?, last_name = ?, 
                    updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
                ''', (username, first_name, last_name, user_id))
                conn.commit()
                
                return User(
                    user_id=row[0],
                    username=row[1],
                    first_name=row[2],
                    last_name=row[3],
                    total_points=row[4],
                    created_at=datetime.fromisoformat(row[5]) if row[5] else None,
                    updated_at=datetime.fromisoformat(row[6]) if row[6] else None
                )
            else:
                # 创建新用户
                cursor.execute('''
                    INSERT INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                
                return User(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    total_points=0,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
    
    def add_points(self, user_id: int, points: int, transaction_type: str, description: str) -> bool:
        """增加用户积分"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 如果是扣除积分，先检查余额是否足够
                if points < 0:
                    cursor.execute('SELECT total_points FROM users WHERE user_id = ?', (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        logger.warning(f"用户 {user_id} 不存在")
                        return False
                    
                    current_points = result[0]
                    if current_points + points < 0:
                        logger.warning(f"用户 {user_id} 积分不足，当前: {current_points}, 尝试扣除: {abs(points)}")
                        return False
                
                # 更新用户总积分
                cursor.execute('''
                    UPDATE users SET total_points = total_points + ?, 
                    updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
                ''', (points, user_id))
                
                # 记录积分交易
                cursor.execute('''
                    INSERT INTO points_transactions (user_id, points_change, transaction_type, description)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, points, transaction_type, description))
                
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"添加积分失败: {e}")
            return False

    def can_checkin_today(self, user_id: int) -> bool:
        """检查用户今天是否可以签到"""
        today = date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM checkin_records
                WHERE user_id = ? AND checkin_date = ?
            ''', (user_id, today))
            count = cursor.fetchone()[0]
            return count < Config.MAX_CHECKIN_PER_DAY

    def record_checkin(self, user_id: int, points: int) -> bool:
        """记录签到"""
        today = date.today().isoformat()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO checkin_records (user_id, checkin_date, points_earned)
                    VALUES (?, ?, ?)
                ''', (user_id, today, points))
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            # 今天已经签到过了
            return False
        except Exception as e:
            logger.error(f"记录签到失败: {e}")
            return False

    def get_daily_message_points(self, user_id: int, group_id: int) -> int:
        """获取用户今天在指定群的发言积分"""
        today = date.today().isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COALESCE(points_earned, 0) FROM message_records
                WHERE user_id = ? AND group_id = ? AND message_date = ?
            ''', (user_id, group_id, today))
            result = cursor.fetchone()
            return result[0] if result else 0

    def record_message(self, user_id: int, group_id: int, points: int) -> bool:
        """记录发言积分"""
        today = date.today().isoformat()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # 尝试更新现有记录
                cursor.execute('''
                    UPDATE message_records
                    SET points_earned = points_earned + ?, message_count = message_count + 1
                    WHERE user_id = ? AND group_id = ? AND message_date = ?
                ''', (points, user_id, group_id, today))

                if cursor.rowcount == 0:
                    # 如果没有现有记录，创建新记录
                    cursor.execute('''
                        INSERT INTO message_records (user_id, group_id, message_date, points_earned)
                        VALUES (?, ?, ?, ?)
                    ''', (user_id, group_id, today, points))

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"记录发言失败: {e}")
            return False

    def get_user_points(self, user_id: int) -> int:
        """获取用户总积分"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT total_points FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def get_user_rank(self, user_id: int) -> tuple:
        """获取用户排名信息 (排名, 总用户数)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 获取用户积分
            user_points = self.get_user_points(user_id)

            # 获取排名
            cursor.execute('''
                SELECT COUNT(*) FROM users WHERE total_points > ?
            ''', (user_points,))
            rank = cursor.fetchone()[0] + 1

            # 获取总用户数
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]

            return rank, total_users

    def get_top_users(self, limit: int = 10) -> List[tuple]:
        """获取积分排行榜"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT user_id, username, first_name, total_points
                FROM users ORDER BY total_points DESC LIMIT ?
            ''', (limit,))
            return cursor.fetchall()
    
    def cleanup_expired_points(self) -> int:
        """清理过期积分，返回清理的用户数量"""
        if Config.POINTS_EXPIRE_DAYS <= 0:
            return 0  # 永不过期
        
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 计算过期时间
                expire_date = datetime.now() - timedelta(days=Config.POINTS_EXPIRE_DAYS)
                expire_date_str = expire_date.strftime('%Y-%m-%d %H:%M:%S')
                
                # 获取所有用户的过期积分
                cursor.execute('''
                    SELECT user_id, 
                           SUM(CASE WHEN points_change > 0 AND created_at < ? THEN points_change ELSE 0 END) as expired_points
                    FROM points_transactions 
                    WHERE created_at < ?
                    GROUP BY user_id
                    HAVING expired_points > 0
                ''', (expire_date_str, expire_date_str))
                
                expired_users = cursor.fetchall()
                cleaned_count = 0
                
                for user_id, expired_points in expired_users:
                    # 获取用户当前积分
                    cursor.execute('SELECT total_points FROM users WHERE user_id = ?', (user_id,))
                    result = cursor.fetchone()
                    if not result:
                        continue
                    
                    current_points = result[0]
                    # 扣除过期积分，但不能低于0
                    points_to_deduct = min(expired_points, current_points)
                    
                    if points_to_deduct > 0:
                        # 扣除过期积分
                        cursor.execute('''
                            UPDATE users SET total_points = total_points - ?, 
                            updated_at = CURRENT_TIMESTAMP WHERE user_id = ?
                        ''', (points_to_deduct, user_id))
                        
                        # 记录积分过期交易
                        cursor.execute('''
                            INSERT INTO points_transactions (user_id, points_change, transaction_type, description)
                            VALUES (?, ?, ?, ?)
                        ''', (user_id, -points_to_deduct, 'expire', f'积分过期清理，过期天数: {Config.POINTS_EXPIRE_DAYS}'))
                        
                        cleaned_count += 1
                        logger.info(f"用户 {user_id} 过期积分已清理: {points_to_deduct}")
                
                conn.commit()
                logger.info(f"积分过期清理完成，共处理 {cleaned_count} 个用户")
                return cleaned_count
                
        except Exception as e:
            logger.error(f"清理过期积分失败: {e}")
            return 0
    
    def record_search_message(self, user_id: int):
        """记录用户在搜索群的发言时间"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 创建搜索群发言记录表（如果不存在）
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS search_message_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        last_message_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id),
                        UNIQUE(user_id)
                    )
                ''')
                
                # 插入或更新用户最后发言时间
                cursor.execute('''
                    INSERT OR REPLACE INTO search_message_records (user_id, last_message_time)
                    VALUES (?, CURRENT_TIMESTAMP)
                ''', (user_id,))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"记录搜索群发言时间失败: {e}")
            return False
    
    def can_send_search_message(self, user_id: int) -> bool:
        """检查用户是否可以在搜索群发言（基于冷却时间）"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 获取用户最后发言时间
                cursor.execute('''
                    SELECT last_message_time FROM search_message_records WHERE user_id = ?
                ''', (user_id,))
                
                result = cursor.fetchone()
                if not result:
                    # 用户从未发言，可以发言
                    return True
                
                last_message_time = datetime.fromisoformat(result[0])
                current_time = datetime.now()
                
                # 计算时间差
                time_diff = current_time - last_message_time
                cooldown_hours = Config.ZERO_POINTS_COOLDOWN_HOURS
                
                # 检查是否超过冷却时间
                return time_diff.total_seconds() >= cooldown_hours * 3600
                
        except Exception as e:
            logger.error(f"检查搜索群发言权限失败: {e}")
            return True  # 出错时允许发言
