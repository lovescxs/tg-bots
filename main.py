#!/usr/bin/env python3
"""
Telegram 积分机器人
功能：
1. 签到群：用户可以签到和发言获取积分
2. VIP群：只有达到积分要求的用户才能发言
"""

import logging
import asyncio
import datetime
from telegram.ext import Application, CommandHandler
from config import Config
from database import Database
from handlers.checkin_handler import CheckinHandler
from handlers.search_handler import SearchHandler

# 配置日志
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        # 验证配置
        Config.validate()
        
        # 初始化数据库
        self.db = Database()
        
        # 初始化处理器
        self.checkin_handler = CheckinHandler(self.db)
        self.search_handler = SearchHandler(self.db)
        
        # 创建应用
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # 注册处理器
        self._register_handlers()
    
    def _register_handlers(self):
        """注册所有消息处理器"""
        
        # 通用命令
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        
        # 管理员命令
        self.application.add_handler(CommandHandler("admin", self.admin_command))
        self.application.add_handler(CommandHandler("unban", self.unban_command))
        self.application.add_handler(CommandHandler("stats", self.stats_command))
        self.application.add_handler(CommandHandler("config", self.config_command))
        
        # 签到群处理器
        for handler in self.checkin_handler.get_handlers():
            self.application.add_handler(handler)
        
        # 搜索群处理器
        for handler in self.search_handler.get_handlers():
            self.application.add_handler(handler)
        
        logger.info("所有处理器注册完成")
    
    async def start_command(self, update, context):
        """开始命令"""
        user = update.effective_user
        chat = update.effective_chat
        
        if chat.type == 'private':
            # 私聊回复
            await update.message.reply_text(
                f"👋 你好 @{user.username or user.first_name}！\n\n"
                f"🤖 我是积分管理机器人\n\n"
                f"📝 功能说明：\n"
                f"• 在签到群可以签到和发言获取积分\n"
                f"• 在搜索群消耗积分进行发言搜索\n\n"
                f"💡 使用 /help 查看详细帮助"
            )
        elif chat.id == Config.CHECKIN_GROUP_ID:
            # 签到群回复
            await update.message.reply_text(
                f"👋 欢迎 @{user.username or user.first_name}！\n\n"
                f"📅 使用 /checkin 进行签到\n"
                f"💎 使用 /points 查看积分\n"
                f"🏆 使用 /rank 查看排行榜"
            )
        elif chat.id == Config.SEARCH_GROUP_ID:
            # 搜索群回复
            user_points = self.db.get_user_points(user.id)
            status = "✅ 可以发言" if user_points >= Config.SEARCH_MESSAGE_COST else "❌ 积分不足"

            await update.message.reply_text(
                f"👋 欢迎 @{user.username or user.first_name}！\n\n"
                f"💎 您的积分：{user_points}\n"
                f"💰 发言消耗：{Config.SEARCH_MESSAGE_COST} 积分/条\n"
                f"📊 状态：{status}"
            )
    
    async def help_command(self, update, context):
        """帮助命令"""
        chat = update.effective_chat
        
        if chat.id == Config.CHECKIN_GROUP_ID:
            help_text = (
                "📚 签到群命令帮助\n\n"
                "🔹 /checkin - 每日签到获取积分\n"
                "🔹 /points - 查看个人积分信息\n"
                "🔹 /rank - 查看积分排行榜\n"
                "🔹 /help - 显示此帮助信息\n\n"
                "💡 积分获取方式：\n"
                f"• 每日签到：{Config.CHECKIN_POINTS_MIN}-{Config.CHECKIN_POINTS_MAX} 积分（随机）\n"
                f"• 群内发言：{Config.MESSAGE_POINTS} 积分/条（每日上限 {Config.MAX_MESSAGE_POINTS_PER_DAY} 积分）\n\n"
                f"💰 搜索群发言：{Config.SEARCH_MESSAGE_COST} 积分/条"
            )
        elif chat.id == Config.SEARCH_GROUP_ID:
            help_text = (
                "📚 搜索群说明\n\n"
                f"🔍 本群为积分消费搜索群组\n"
                f"💰 发言消耗：{Config.SEARCH_MESSAGE_COST} 积分/条\n"
                f"💡 只要有积分就可以发言搜索\n"
                f"📈 请前往签到群获取积分\n\n"
                f"📊 使用 /start 查看个人状态"
            )
        else:
            help_text = (
                "📚 机器人帮助\n\n"
                "🤖 我是积分管理机器人\n\n"
                "📝 功能说明：\n"
                "• 签到群：签到和发言获取积分\n"
                "• 搜索群：消耗积分进行发言搜索\n\n"
                "💡 请加入相应群组使用功能"
            )
        
        await update.message.reply_text(help_text)
    
    async def admin_command(self, update, context):
        """管理员命令"""
        user = update.effective_user
        
        # 检查管理员权限
        if user.id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("❌ 您没有管理员权限")
            return
        
        # 解析命令参数
        args = context.args
        if not args:
            await update.message.reply_text(
                "🔧 管理员命令帮助\n\n"
                "• /admin add_points <用户ID> <积分> - 给用户添加积分\n"
                "• /admin user_info <用户ID> - 查看用户信息\n"
                "• /unban [用户ID] - 解除用户禁言（可回复消息使用）\n"
                "• /stats - 查看系统统计\n"
                "• /config - 查看和修改系统配置"
            )
            return
        
        command = args[0]
        
        if command == "add_points" and len(args) >= 3:
            try:
                user_id = int(args[1])
                points = int(args[2])
                
                if self.db.add_points(user_id, points, 'admin_adjust', f'管理员调整: +{points}'):
                    total_points = self.db.get_user_points(user_id)
                    await update.message.reply_text(
                        f"✅ 成功给用户 {user_id} 添加 {points} 积分\n"
                        f"💎 用户总积分：{total_points}"
                    )
                else:
                    await update.message.reply_text("❌ 添加积分失败")
            except ValueError:
                await update.message.reply_text("❌ 参数格式错误")
        
        elif command == "user_info" and len(args) >= 2:
            try:
                user_id = int(args[1])
                points = self.db.get_user_points(user_id)
                rank, total_users = self.db.get_user_rank(user_id)
                
                await update.message.reply_text(
                    f"👤 用户 {user_id} 信息\n\n"
                    f"💎 总积分：{points}\n"
                    f"🏆 排名：{rank}/{total_users}\n"
                    f"🔍 搜索群发言：{'✅ 可以发言' if points >= Config.SEARCH_MESSAGE_COST else '❌ 积分不足'}"
                )
            except ValueError:
                await update.message.reply_text("❌ 用户ID格式错误")
        

    async def unban_command(self, update, context):
        """解禁命令"""
        user = update.effective_user
        
        # 检查管理员权限
        if user.id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("❌ 您没有管理员权限")
            return
        
        try:
            user_id = None
            
            # 检查是否是回复消息
            if update.message.reply_to_message:
                user_id = update.message.reply_to_message.from_user.id
            elif context.args and len(context.args) >= 1:
                user_id = int(context.args[0])
            else:
                await update.message.reply_text("❌ 请回复要解禁的用户消息，或使用 /unban <用户ID>")
                return
            
            # 恢复用户在搜索群的所有权限
            from telegram import ChatPermissions
            unrestricted_permissions = ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
            
            await context.bot.restrict_chat_member(
                chat_id=Config.SEARCH_GROUP_ID,
                user_id=user_id,
                permissions=unrestricted_permissions
            )
            
            # 获取用户名用于显示
            username = "未知用户"
            if update.message.reply_to_message:
                replied_user = update.message.reply_to_message.from_user
                username = f"@{replied_user.username}" if replied_user.username else replied_user.first_name
            
            await update.message.reply_text(
                f"✅ 已解除用户 {username} ({user_id}) 的禁言状态\n"
                f"🔓 用户现在可以在搜索群正常发言"
            )
            
            # 尝试通知用户
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text="🎉 您在搜索群的禁言已被管理员解除！\n\n"
                         "现在您可以正常发言了。请注意保持足够的积分以避免再次被限制。"
                )
            except Exception as e:
                logger.warning(f"无法向用户 {user_id} 发送解禁通知: {e}")
            
        except ValueError:
            await update.message.reply_text("❌ 用户ID格式错误")
        except Exception as e:
            logger.error(f"解禁用户失败: {e}")
            await update.message.reply_text("❌ 解禁失败，请检查用户ID或权限设置")
    
    async def stats_command(self, update, context):
        """统计命令"""
        user = update.effective_user
        
        # 检查管理员权限
        if user.id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("❌ 您没有管理员权限")
            return
        
        # 获取统计数据
        top_users = self.db.get_top_users(5)
        total_users = len(self.db.get_top_users(999999))  # 获取所有用户数量
        
        # 计算有积分用户数量
        active_count = 0
        for _, _, _, points in self.db.get_top_users(999999):
            if points >= Config.SEARCH_MESSAGE_COST:
                active_count += 1
        
        stats_text = (
            f"📊 系统统计\n\n"
            f"👥 总用户数：{total_users}\n"
            f"� 有积分用户：{active_count}\n"
            f"📈 活跃率：{active_count/total_users*100:.1f}%\n\n"
            f"🏆 TOP 5 用户：\n"
        )
        
        for i, (user_id, username, first_name, points) in enumerate(top_users, 1):
            display_name = username or first_name or f"用户{user_id}"
            stats_text += f"{i}. @{display_name}: {points} 积分\n"
        
        await update.message.reply_text(stats_text)

    async def config_command(self, update, context):
        """配置管理命令"""
        user = update.effective_user

        # 检查管理员权限
        if user.id not in Config.ADMIN_USER_IDS:
            await update.message.reply_text("❌ 您没有管理员权限")
            return

        # 解析命令参数
        args = context.args
        if not args:
            # 显示当前配置
            config_info = Config.get_config_info()
            expire_text = "永不过期" if config_info['expire_days'] == 0 else f"{config_info['expire_days']}天"
            config_text = (
                "⚙️ 当前系统配置\n\n"
                f"🎲 签到积分范围：{config_info['checkin_min']}-{config_info['checkin_max']}\n"
                f"💬 发言积分：{config_info['message_points']}\n"
                f"💰 搜索群发言消耗：{config_info['search_cost']}\n"
                f"📊 每日发言积分上限：{config_info['max_daily_points']}\n"
                f"⏰ 积分过期时间：{expire_text}\n"
                f"🕐 积分为0时发言限制：{config_info['cooldown_hours']}小时一次\n\n"
                "🔧 修改配置命令：\n"
                "• /config checkin_min <数值> - 设置签到最少积分\n"
                "• /config checkin_max <数值> - 设置签到最多积分\n"
                "• /config message_points <数值> - 设置发言积分\n"
                "• /config search_cost <数值> - 设置搜索群发言消耗\n"
                "• /config max_daily_points <数值> - 设置每日发言积分上限\n"
                "• /config expire_days <数值> - 设置积分过期天数（0为永不过期）\n"
                "• /config cooldown_hours <数值> - 设置积分为0时发言冷却时间（小时）"
            )
            await update.message.reply_text(config_text)
            return

        if len(args) >= 2:
            config_key = args[0]
            try:
                config_value = int(args[1])

                if Config.update_config(config_key, config_value):
                    await update.message.reply_text(
                        f"✅ 配置更新成功\n"
                        f"🔧 {config_key}: {config_value}"
                    )
                    logger.info(f"管理员 {user.id} 更新配置: {config_key} = {config_value}")
                else:
                    await update.message.reply_text(
                        f"❌ 无效的配置项: {config_key}\n"
                        f"💡 使用 /config 查看可用配置项"
                    )
            except ValueError:
                await update.message.reply_text("❌ 配置值必须是数字")
        else:
            await update.message.reply_text("❌ 参数不足，使用 /config 查看帮助")

    async def cleanup_expired_points_job(self, context):
        """定期清理过期积分的任务"""
        try:
            cleaned_count = self.db.cleanup_expired_points()
            if cleaned_count > 0:
                logger.info(f"定期清理完成，处理了 {cleaned_count} 个用户的过期积分")
        except Exception as e:
            logger.error(f"定期清理过期积分失败: {e}")
    
    def run(self):
        """运行机器人"""
        logger.info("机器人启动中...")
        logger.info(f"签到群ID: {Config.CHECKIN_GROUP_ID}")
        logger.info(f"搜索群ID: {Config.SEARCH_GROUP_ID}")
        logger.info(f"签到积分: {Config.CHECKIN_POINTS_MIN}-{Config.CHECKIN_POINTS_MAX}")
        logger.info(f"搜索群发言消耗: {Config.SEARCH_MESSAGE_COST} 积分")
        logger.info(f"积分过期天数: {Config.POINTS_EXPIRE_DAYS} ({'永不过期' if Config.POINTS_EXPIRE_DAYS == 0 else '天'})")
        
        # 添加定期清理过期积分的任务（每天凌晨2点执行）
        if Config.POINTS_EXPIRE_DAYS > 0:
            job_queue = self.application.job_queue
            job_queue.run_daily(
                self.cleanup_expired_points_job,
                time=datetime.time(2, 0),  # 每天凌晨2点
                name="cleanup_expired_points"
            )
            logger.info("已启动积分过期清理定时任务（每天凌晨2点执行）")
        
        # 运行机器人
        self.application.run_polling(drop_pending_updates=True)

def main():
    """主函数"""
    try:
        bot = TelegramBot()
        bot.run()
    except Exception as e:
        logger.error(f"机器人启动失败: {e}")
        raise

if __name__ == "__main__":
    main()
