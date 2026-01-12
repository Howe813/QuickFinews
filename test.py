#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickFinews 测试脚本
用于测试 TuShare 接口和电报机器人连接
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import tushare as ts
from telegram import Bot
from telegram.error import TelegramError
import asyncio

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 新闻来源列表
NEWS_SOURCES = ['sina', 'wallstreetcn', '10jqka', 'eastmoney', 'yuncaijing', 'fenghuang', 'jinrongjie', 'cls', 'yicai']

# 来源名称映射
SOURCE_NAMES = {
    'sina': '新浪财经',
    'wallstreetcn': '华尔街见闻',
    '10jqka': '同花顺',
    'eastmoney': '东方财富',
    'yuncaijing': '云财经',
    'fenghuang': '凤凰新闻',
    'jinrongjie': '金融界',
    'cls': '财联社',
    'yicai': '第一财经'
}


def test_tushare(token: str):
    """测试 TuShare 连接"""
    logger.info("=" * 50)
    logger.info("测试 TuShare 连接")
    logger.info("=" * 50)
    
    try:
        ts.set_token(token)
        pro = ts.pro_api()
        
        # 获取最近 1 小时的新闻
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)
        
        start_date = start_time.strftime('%Y-%m-%d %H:%M:%S')
        end_date = end_time.strftime('%Y-%m-%d %H:%M:%S')
        
        logger.info(f"获取时间范围: {start_date} 到 {end_date}")
        
        # 测试每个来源
        total_news = 0
        for source in NEWS_SOURCES:
            try:
                logger.info(f"测试来源: {SOURCE_NAMES.get(source, source)}")
                df = pro.news(src=source, start_date=start_date, end_date=end_date)
                
                if df is not None and not df.empty:
                    count = len(df)
                    total_news += count
                    logger.info(f"  ✓ {SOURCE_NAMES.get(source, source)}: 获取了 {count} 条新闻")
                    
                    # 显示第一条新闻
                    first_news = df.iloc[0]
                    logger.info(f"    标题: {first_news.get('title', 'N/A')}")
                    logger.info(f"    时间: {first_news.get('datetime', 'N/A')}")
                else:
                    logger.info(f"  ℹ {SOURCE_NAMES.get(source, source)}: 未获取到新闻")
            except Exception as e:
                logger.error(f"  ✗ {SOURCE_NAMES.get(source, source)}: 获取失败 - {e}")
        
        logger.info(f"总共获取了 {total_news} 条新闻")
        logger.info("✓ TuShare 连接测试成功")
        return True
        
    except Exception as e:
        logger.error(f"✗ TuShare 连接测试失败: {e}")
        return False


async def test_telegram(token: str, chat_id: str):
    """测试电报连接"""
    logger.info("=" * 50)
    logger.info("测试电报连接")
    logger.info("=" * 50)
    
    try:
        bot = Bot(token=token)
        
        # 获取机器人信息
        me = await bot.get_me()
        logger.info(f"机器人用户名: @{me.username}")
        logger.info(f"机器人名称: {me.first_name}")
        
        # 发送测试消息
        test_message = """
<b>🧪 QuickFinews 测试消息</b>

这是一条测试消息，用于验证电报机器人连接是否正常。

<i>如果您看到这条消息，说明配置成功！</i>
"""
        
        logger.info(f"发送测试消息到 Chat ID: {chat_id}")
        await bot.send_message(
            chat_id=chat_id,
            text=test_message,
            parse_mode='HTML'
        )
        
        logger.info("✓ 电报连接测试成功")
        return True
        
    except TelegramError as e:
        logger.error(f"✗ 电报连接测试失败: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ 电报连接测试失败: {e}")
        return False


async def main():
    """主测试函数"""
    logger.info("QuickFinews 测试套件")
    logger.info("=" * 50)
    
    # 从环境变量读取配置
    tushare_token = os.getenv('TUSHARE_TOKEN')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    # 验证配置
    if not tushare_token:
        logger.error("未设置 TUSHARE_TOKEN 环境变量")
        sys.exit(1)
    
    if not telegram_token:
        logger.error("未设置 TELEGRAM_TOKEN 环境变量")
        sys.exit(1)
    
    if not telegram_chat_id:
        logger.error("未设置 TELEGRAM_CHAT_ID 环境变量")
        sys.exit(1)
    
    logger.info(f"TuShare Token: {tushare_token[:10]}...")
    logger.info(f"Telegram Token: {telegram_token[:10]}...")
    logger.info(f"Telegram Chat ID: {telegram_chat_id}")
    logger.info("=" * 50)
    
    # 运行测试
    results = {}
    
    # 测试 TuShare
    results['tushare'] = test_tushare(tushare_token)
    logger.info("")
    
    # 测试电报
    results['telegram'] = await test_telegram(telegram_token, telegram_chat_id)
    logger.info("")
    
    # 总结
    logger.info("=" * 50)
    logger.info("测试总结")
    logger.info("=" * 50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✓ 通过" if passed else "✗ 失败"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    logger.info("=" * 50)
    
    if all_passed:
        logger.info("✓ 所有测试通过！应用已准备好运行。")
        sys.exit(0)
    else:
        logger.error("✗ 部分测试失败，请检查配置。")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
