# Telegram 积分机器人

一个功能完整的Telegram机器人，实现签到积分系统和基于积分的群组发言权限控制。

## 功能特性

### 签到群功能
- ✅ 每日签到获取积分
- ✅ 发言获取积分（有每日上限）
- ✅ 积分查询和排行榜
- ✅ 用户排名系统

### 搜索群功能
- ✅ 积分消费制发言搜索（有积分就能发言）
- ✅ 每次发言自动扣除积分
- ✅ 自动删除积分不足用户的消息
- ✅ 积分不足自动禁言（可配置时长）
- ✅ 新成员加入提醒
- ✅ 私聊/群内提醒系统

### 管理功能
- ✅ 管理员积分调整
- ✅ 用户信息查询
- ✅ 用户解禁功能（支持回复消息）
- ✅ 系统统计数据
- ✅ 动态配置修改（私聊机器人）
- ✅ 完整的日志记录

## 安装部署

### 1. 环境要求
- Python 3.8+
- pip

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

## 详细配置说明

### 🔧 基础配置

#### BOT_TOKEN（必需）
- **描述**: Telegram Bot API Token
- **获取方式**: 通过 [@BotFather](https://t.me/BotFather) 创建机器人获得
- **示例**: `BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### 🏘️ 群组配置

#### CHECKIN_GROUP_ID（必需）
- **描述**: 签到群的群组ID（负数）
- **功能**: 用户在此群进行签到和日常聊天获取积分
- **示例**: `CHECKIN_GROUP_ID=-1002231439786`

#### SEARCH_GROUP_ID（必需）
- **描述**: 搜索群的群组ID（负数）
- **功能**: 需要消耗积分才能发言的高级群组
- **示例**: `SEARCH_GROUP_ID=-1002450242353`

### 💎 积分系统配置

#### 签到积分配置
- `CHECKIN_POINTS_MIN=5` - 每日签到获得的最少积分
- `CHECKIN_POINTS_MAX=10` - 每日签到获得的最多积分（实际获得积分在最小值和最大值之间随机）
- `MAX_CHECKIN_PER_DAY=1` - 每日最大签到次数

#### 发言积分配置
- `MESSAGE_POINTS=1` - 在签到群发言获得的积分
- `MAX_MESSAGE_POINTS_PER_DAY=10` - 每日通过发言获得的最大积分
- `SEARCH_MESSAGE_COST=1` - 在搜索群发言消耗的积分

#### 积分过期配置
- `POINTS_EXPIRE_DAYS=0` - 积分过期天数（0表示永不过期）

#### 禁言配置
- `ZERO_POINTS_COOLDOWN_HOURS=1` - 积分为0时的发言冷却时间（小时）
- `BAN_DURATION_HOURS=1` - 积分不足时的禁言时长（小时）

### 👨‍💼 管理员配置
- `ADMIN_USER_IDS=123456789,987654321` - 管理员用户ID列表（用逗号分隔）

### 🗄️ 数据库配置
- `DATABASE_PATH=bot_data.db` - SQLite 数据库文件路径

### 📝 完整配置示例

```env
# 机器人Token（必需）
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 群组配置（必需）
CHECKIN_GROUP_ID=-1001234567890
SEARCH_GROUP_ID=-1001234567891

# 积分配置
CHECKIN_POINTS_MIN=5
CHECKIN_POINTS_MAX=15
MESSAGE_POINTS=2
SEARCH_MESSAGE_COST=3
MAX_CHECKIN_PER_DAY=1
MAX_MESSAGE_POINTS_PER_DAY=20

# 积分过期和禁言配置
POINTS_EXPIRE_DAYS=30
ZERO_POINTS_COOLDOWN_HOURS=1
BAN_DURATION_HOURS=2

# 管理员配置
ADMIN_USER_IDS=123456789,987654321

# 数据库配置
DATABASE_PATH=bot_data.db
```

### 4. 获取群组ID
1. 将机器人添加到群组
2. 发送消息到群组
3. 访问 `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
4. 在返回的JSON中找到 `chat.id`（负数）

### 5. 运行机器人
```bash
python main.py
```

## 使用说明

### 用户命令

#### 签到群命令
- `/checkin` - 每日签到获取积分
- `/points` - 查看个人积分信息
- `/rank` - 查看积分排行榜
- `/help` - 显示帮助信息

#### 搜索群
- 只要有积分就可以发言搜索
- 每次发言自动扣除1积分
- 积分不足的消息会被自动删除
- 新成员加入时会显示积分状态

### 管理员命令（私聊机器人使用）
- `/admin add_points <用户ID> <积分>` - 给用户添加积分
- `/admin user_info <用户ID>` - 查看用户信息
- `/unban [用户ID]` - 解除用户禁言（可回复消息使用）
- `/stats` - 查看系统统计
- `/config` - 查看和修改系统配置

## 积分规则

### 获取积分
- **每日签到**：5-10积分随机（每天限1次）
- **群内发言**：1积分/条（每日上限10积分）

### 搜索群发言
- **发言条件**：只要有积分就可以发言搜索
- **消费规则**：每次发言扣除1积分
- **权限检查**：每次发言时检查积分
- **消息处理**：积分不足的消息自动删除
- **禁言机制**：积分不足用户自动禁言（默认1小时，可配置）
- **解禁方式**：管理员可使用 `/unban` 命令手动解禁

### 配置管理
- **动态调整**：管理员可通过私聊机器人修改所有积分规则
- **实时生效**：配置修改后立即生效
- **可调参数**：签到积分范围、发言积分、搜索群消费、每日上限等

## 项目结构

```
.
├── main.py                 # 主程序入口
├── config.py              # 配置管理
├── database.py            # 数据库操作
├── models.py              # 数据模型
├── handlers/              # 消息处理器
│   ├── __init__.py
│   ├── checkin_handler.py # 签到群处理器
│   └── search_handler.py  # 搜索群处理器
├── requirements.txt       # Python依赖
├── .env.example          # 环境变量示例
├── README.md             # 项目说明
└── bot.log               # 运行日志（自动生成）
```

## 数据库设计

使用SQLite数据库，包含以下表：

- `users` - 用户信息表
- `checkin_records` - 签到记录表
- `message_records` - 发言记录表
- `points_transactions` - 积分交易记录表

## 注意事项

1. **机器人权限**：确保机器人在搜索群有以下权限：
   - 删除消息权限（删除积分不足的消息）
   - 限制成员权限（禁言功能）
2. **群组类型**：支持超级群组（Supergroup）
3. **数据备份**：定期备份 `bot_data.db` 文件
4. **日志监控**：查看 `bot.log` 了解运行状态
5. **安全性**：不要泄露 `.env` 文件中的敏感信息
6. **禁言配置**：合理设置禁言时长，避免过度限制用户

## 常见问题

### Q: 机器人无法删除消息或禁言用户？
A: 检查机器人是否有管理员权限，特别是"删除消息"和"限制成员"权限。

### Q: 如何修改禁言时长？
A: 在 `.env` 文件中修改 `BAN_DURATION_HOURS` 配置项，重启机器人生效。

### Q: 如何手动解禁用户？
A: 管理员可以使用 `/unban` 命令，支持两种方式：
   - 回复被禁言用户的消息，然后发送 `/unban`
   - 直接使用 `/unban <用户ID>` 指定用户ID

### Q: 如何修改积分规则？
A: 修改 `.env` 文件中的相关配置项，重启机器人生效。

### Q: 如何备份数据？
A: 复制 `bot_data.db` 文件即可备份所有用户数据。

### Q: 如何添加新的管理员？
A: 在 `.env` 文件的 `ADMIN_USER_IDS` 中添加用户ID，用逗号分隔。

## 技术支持

如有问题或建议，请提交Issue或联系开发者。

## 许可证

MIT License
