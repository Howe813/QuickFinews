#!/bin/bash

# QuickFinews 部署脚本
# 用于在 Linux 服务器上部署应用

set -e

echo "================================"
echo "QuickFinews 部署脚本"
echo "================================"

# 检查 Python 版本
echo "检查 Python 版本..."
python3 --version

# 检查 pip
echo "检查 pip..."
pip3 --version

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "警告: 未找到 .env 文件"
    echo "请复制 .env.example 为 .env 并填入配置"
    echo ""
    echo "cp .env.example .env"
    echo "nano .env"
    exit 1
fi

# 运行测试
echo ""
echo "运行测试..."
python3 test.py

if [ $? -ne 0 ]; then
    echo "测试失败，请检查配置"
    exit 1
fi

# 创建 systemd 服务
echo ""
echo "创建 systemd 服务..."

SERVICE_FILE="/etc/systemd/system/quickfinews.service"
WORK_DIR=$(pwd)
PYTHON_PATH=$(which python3)

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=QuickFinews - Financial News Real-time Push Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORK_DIR
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$WORK_DIR/.env
ExecStart=$PYTHON_PATH $WORK_DIR/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ 服务文件已创建: $SERVICE_FILE"

# 重新加载 systemd
echo "重新加载 systemd..."
sudo systemctl daemon-reload

# 启用服务
echo "启用服务..."
sudo systemctl enable quickfinews

# 启动服务
echo "启动服务..."
sudo systemctl start quickfinews

# 检查服务状态
echo ""
echo "检查服务状态..."
sudo systemctl status quickfinews

echo ""
echo "================================"
echo "部署完成！"
echo "================================"
echo ""
echo "常用命令:"
echo "  查看日志:       sudo journalctl -u quickfinews -f"
echo "  停止服务:       sudo systemctl stop quickfinews"
echo "  启动服务:       sudo systemctl start quickfinews"
echo "  重启服务:       sudo systemctl restart quickfinews"
echo "  查看状态:       sudo systemctl status quickfinews"
echo ""
