# QuickFinews 快速开始指南

本指南将帮助您快速部署和运行 QuickFinews 财经新闻推送机器人。

## 前提条件

- ✅ TuShare API Token（已配置）
- ✅ 电报机器人 Token（已配置）
- ✅ 电报群组 Chat ID（已配置）
- 🖥️ 一台 Linux 服务器（推荐 Ubuntu 20.04+）
- 🐍 Python 3.7+

## 快速部署（5 分钟）

### 步骤 1：克隆仓库

```bash
git clone https://github.com/Howe813/QuickFinews.git
cd QuickFinews
```

### 步骤 2：安装依赖

```bash
pip3 install -r requirements.txt
```

或使用 sudo（如果遇到权限问题）：

```bash
sudo pip3 install -r requirements.txt
```

### 步骤 3：配置环境变量

复制配置模板：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入您的配置：

```bash
nano .env
```

配置内容：

```env
# TuShare 配置
TUSHARE_TOKEN=cb63c2545f544191b75f8bebc53f14d606ae81494a5c06b491a72611

# 电报机器人配置
TELEGRAM_TOKEN=8525895709:AAECjlC0G2isTdROfsucAA0rPUHFuN5JI5Q
TELEGRAM_CHAT_ID=-1003465767625

# 检查间隔（秒）
CHECK_INTERVAL=60
```

保存并退出（Ctrl+X，然后按 Y，再按 Enter）。

### 步骤 4：运行测试

```bash
export $(cat .env | xargs)
python3 test.py
```

如果测试通过，您会看到：

```
✓ 所有测试通过！应用已准备好运行。
```

### 步骤 5：启动应用

#### 方式 1：前台运行（测试用）

```bash
export $(cat .env | xargs)
python3 main.py
```

按 `Ctrl+C` 停止。

#### 方式 2：后台运行（推荐）

```bash
nohup python3 main.py > quickfinews.log 2>&1 &
```

查看日志：

```bash
tail -f quickfinews.log
```

停止应用：

```bash
pkill -f main.py
```

#### 方式 3：使用 systemd 服务（生产环境推荐）

运行自动部署脚本：

```bash
chmod +x deploy.sh
./deploy.sh
```

这将自动：
- 安装依赖
- 运行测试
- 创建 systemd 服务
- 启动服务

管理服务：

```bash
# 查看状态
sudo systemctl status quickfinews

# 查看日志
sudo journalctl -u quickfinews -f

# 停止服务
sudo systemctl stop quickfinews

# 启动服务
sudo systemctl start quickfinews

# 重启服务
sudo systemctl restart quickfinews
```

## 验证运行

应用启动后，您应该在电报群组中看到新闻推送。

检查日志：

```bash
tail -f quickfinews.log
```

您应该看到类似的输出：

```
2024-01-12 10:30:45,123 - __main__ - INFO - QuickFinews - 财经新闻实时推送机器人
2024-01-12 10:30:45,456 - __main__ - INFO - 检查新闻: 2024-01-12 10:25:45 到 2024-01-12 10:30:45
2024-01-12 10:30:48,012 - __main__ - INFO - 从 新浪财经 获取了 5 条新闻
2024-01-12 10:30:49,345 - __main__ - INFO - 消息已发送到电报
```

## 配置调优

### 调整检查间隔

编辑 `.env` 文件，修改 `CHECK_INTERVAL` 值（单位：秒）：

```env
# 每 30 秒检查一次
CHECK_INTERVAL=30

# 每 5 分钟检查一次
CHECK_INTERVAL=300
```

**注意**：TuShare API 有速率限制（每分钟最多访问 1 次），建议间隔不要小于 60 秒。

### 修改新闻来源

编辑 `main.py` 文件，修改 `NEWS_SOURCES` 列表：

```python
# 只获取新浪财经和华尔街见闻
NEWS_SOURCES = ['sina', 'wallstreetcn']

# 获取所有来源
NEWS_SOURCES = ['sina', 'wallstreetcn', '10jqka', 'eastmoney', 'yuncaijing', 'fenghuang', 'jinrongjie', 'cls', 'yicai']
```

## 常见问题

### 1. TuShare API 报错："每分钟最多访问该接口1次"

**原因**：TuShare API 有速率限制。

**解决方案**：
- 增加 `CHECK_INTERVAL` 值（建议 60 秒以上）
- 应用会自动处理速率限制，继续运行即可

### 2. 电报消息发送失败

**原因**：机器人未添加到群组，或 Chat ID 错误。

**解决方案**：
- 确保机器人已添加到群组
- 确保机器人有发送消息的权限
- 重新获取 Chat ID

### 3. 没有收到新闻推送

**可能原因**：
- 时间段内没有新闻
- TuShare API 限制
- 新闻已经推送过（去重机制）

**解决方案**：
- 查看日志确认应用运行状态
- 删除 `news_history.json` 重新开始
- 调整检查间隔

### 4. 内存占用过高

**解决方案**：
- 定期清理 `news_history.json` 文件
- 减少检查频率
- 限制新闻来源数量

## Docker 部署（可选）

### 使用 Docker Compose

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

### 使用 Docker

```bash
# 构建镜像
docker build -t quickfinews .

# 运行容器
docker run -d \
  --name quickfinews \
  --env-file .env \
  quickfinews

# 查看日志
docker logs -f quickfinews

# 停止容器
docker stop quickfinews
```

## 监控和维护

### 定期检查日志

```bash
# 查看最近 100 行日志
tail -n 100 quickfinews.log

# 实时查看日志
tail -f quickfinews.log
```

### 日志轮转

创建 `/etc/logrotate.d/quickfinews`：

```
/home/ubuntu/QuickFinews/quickfinews.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 ubuntu ubuntu
}
```

### 定期清理历史记录

```bash
# 备份历史记录
cp news_history.json news_history.json.bak

# 清空历史记录
echo '{"ids": []}' > news_history.json
```

## 更新应用

```bash
# 拉取最新代码
git pull

# 重启服务
sudo systemctl restart quickfinews

# 或重启 Docker 容器
docker-compose restart
```

## 获取帮助

如有问题，请：
1. 查看日志文件 `quickfinews.log`
2. 运行测试脚本 `python3 test.py`
3. 在 GitHub 提交 Issue：https://github.com/Howe813/QuickFinews/issues

## 下一步

- 📊 添加新闻统计功能
- 🔍 添加关键词过滤
- 📧 添加邮件通知
- 🌐 添加 Web 管理界面

祝您使用愉快！🎉
