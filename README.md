# QuickFinews - 财经新闻实时推送机器人

一个集成 **TuShare 新闻接口**和**电报机器人**的 Python 应用，实现财经新闻的实时推送功能。

## 功能特性

- 🚀 **实时推送**：监听多个财经新闻来源，有新闻立即推送到电报
- 📰 **多源支持**：支持 9 个主流财经新闻来源
  - 新浪财经
  - 华尔街见闻
  - 同花顺
  - 东方财富
  - 云财经
  - 凤凰新闻
  - 金融界
  - 财联社
  - 第一财经
- 🔄 **去重机制**：自动记录已推送新闻，避免重复推送
- 📊 **历史记录**：保存推送历史，便于追踪
- 🛡️ **错误处理**：完善的错误处理和日志记录
- ⚙️ **可配置**：灵活的配置选项和检查间隔

## 系统要求

- Python 3.7+
- 有效的 TuShare API Token
- 有效的电报机器人 Token
- 互联网连接

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Howe813/QuickFinews.git
cd QuickFinews
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，并填入你的配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```env
# TuShare 配置
TUSHARE_TOKEN=your_tushare_token

# 电报机器人配置
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# 检查间隔（秒）
CHECK_INTERVAL=60
```

### 获取必要的 Token

#### TuShare Token
1. 访问 [TuShare 官网](https://tushare.pro)
2. 注册账户
3. 在用户中心获取 API Token
4. 申请 `news` 接口权限

#### 电报机器人 Token
1. 在 Telegram 中搜索 `@BotFather`
2. 发送 `/newbot` 命令创建新机器人
3. 按照提示填写机器人名称和用户名
4. 获取 Token

#### 电报 Chat ID
1. 创建一个电报频道或群组
2. 将机器人添加到频道/群组
3. 发送一条消息到频道/群组
4. 访问 `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates` 获取 Chat ID

## 使用方法

### 直接运行

```bash
python main.py
```

### 使用 .env 文件

```bash
# 确保 .env 文件在项目根目录
python main.py
```

### 后台运行（使用 nohup）

```bash
nohup python main.py > quickfinews.log 2>&1 &
```

### 使用 systemd 服务（Linux）

创建 `/etc/systemd/system/quickfinews.service`：

```ini
[Unit]
Description=QuickFinews - Financial News Real-time Push Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/QuickFinews
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=/home/ubuntu/QuickFinews/.env
ExecStart=/usr/bin/python3 /home/ubuntu/QuickFinews/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable quickfinews
sudo systemctl start quickfinews
```

查看日志：

```bash
sudo journalctl -u quickfinews -f
```

## 项目结构

```
QuickFinews/
├── main.py                 # 主应用文件
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
├── README.md              # 项目文档
├── quickfinews.log        # 应用日志（运行时生成）
└── news_history.json      # 新闻历史记录（运行时生成）
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 必需 | 示例 |
|--------|------|------|------|
| `TUSHARE_TOKEN` | TuShare API Token | 是 | `cb63c2545f544191b75f8bebc53f14d606ae81494a5c06b491a72611` |
| `TELEGRAM_TOKEN` | 电报机器人 Token | 是 | `8525895709:AAECjlC0G2isTdROfsucAA0rPUHFuN5JI5Q` |
| `TELEGRAM_CHAT_ID` | 电报频道/群组 ID | 是 | `-1001234567890` |
| `CHECK_INTERVAL` | 检查间隔（秒） | 否 | `60` |

### 新闻来源

应用支持以下新闻来源：

| 来源 | 标识 | 描述 |
|------|------|------|
| 新浪财经 | sina | 新浪财经实时资讯 |
| 华尔街见闻 | wallstreetcn | 华尔街见闻快讯 |
| 同花顺 | 10jqka | 同花顺财经新闻 |
| 东方财富 | eastmoney | 东方财富财经新闻 |
| 云财经 | yuncaijing | 云财经新闻 |
| 凤凰新闻 | fenghuang | 凤凰新闻 |
| 金融界 | jinrongjie | 金融界新闻 |
| 财联社 | cls | 财联社快讯 |
| 第一财经 | yicai | 第一财经快讯 |

## 工作原理

1. **初始化**：应用启动时加载历史记录，防止重复推送
2. **定期检查**：按照设定的间隔（默认 60 秒）检查新闻
3. **获取新闻**：从 TuShare 获取所有来源的最新新闻
4. **去重处理**：检查新闻是否已推送过
5. **实时推送**：将新闻推送到电报频道/群组
6. **记录保存**：保存已推送新闻的历史记录

## 日志说明

应用会生成 `quickfinews.log` 日志文件，记录所有操作：

```
2024-01-12 10:30:45,123 - __main__ - INFO - QuickFinews - 财经新闻实时推送机器人
2024-01-12 10:30:45,456 - __main__ - INFO - 加载了 150 条历史新闻记录
2024-01-12 10:30:46,789 - __main__ - INFO - 检查新闻: 2024-01-12 10:25:45 到 2024-01-12 10:30:45
2024-01-12 10:30:48,012 - __main__ - INFO - 从 新浪财经 获取了 5 条新闻
2024-01-12 10:30:49,345 - __main__ - INFO - 消息已发送到电报 (Chat ID: -1001234567890)
```

## 故障排除

### 问题：无法连接到 TuShare

**解决方案**：
- 检查网络连接
- 验证 API Token 是否正确
- 确保已申请 `news` 接口权限

### 问题：电报消息无法发送

**解决方案**：
- 验证 Telegram Token 是否正确
- 检查 Chat ID 是否正确
- 确保机器人已被添加到频道/群组
- 检查机器人是否有发送消息的权限

### 问题：内存占用过高

**解决方案**：
- 减少 `CHECK_INTERVAL` 的值（更频繁地检查）
- 清理 `news_history.json` 文件（定期备份后删除）
- 增加服务器内存

### 问题：重复推送新闻

**解决方案**：
- 检查 `news_history.json` 是否被正确保存
- 确保应用有写入权限
- 重启应用

## 性能优化

1. **调整检查间隔**：根据需求调整 `CHECK_INTERVAL`
   - 更频繁的检查：降低 `CHECK_INTERVAL` 值
   - 更少的 API 调用：增加 `CHECK_INTERVAL` 值

2. **历史记录管理**：定期备份并清理 `news_history.json`

3. **日志管理**：定期轮转 `quickfinews.log` 文件

## 部署建议

### 云服务器部署

1. **使用 systemd 服务**（推荐）
2. **使用 Docker 容器**
3. **使用进程管理器**（如 supervisor）

### Docker 部署

创建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY .env .

CMD ["python", "main.py"]
```

构建和运行：

```bash
docker build -t quickfinews .
docker run -d --name quickfinews quickfinews
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

## 更新日志

### v1.0.0 (2024-01-12)
- 初始版本发布
- 支持 9 个新闻来源
- 实现实时推送功能
- 完善的错误处理和日志记录
