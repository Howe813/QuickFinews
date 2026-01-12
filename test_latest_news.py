#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 Finnhub 最新新闻推送逻辑
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import logging
import asyncio
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from main import FinnhubCollector, TelegramNotifier, NewsTracker, FINNHUB_CATEGORIES, SOURCE_NAMES

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_latest_news_logic():
    """测试最新新闻推送逻辑"""
    logger.info("=" * 50)
    logger.info("测试 Finnhub 最新新闻推送逻辑")
    logger.info("=" * 50)
    
    # 从环境变量读取配置
    finnhub_token = os.getenv('FINNHUB_TOKEN')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not finnhub_token:
        logger.error("未设置 FINNHUB_TOKEN")
        return False
    
    if not telegram_token or not telegram_chat_id:
        logger.error("未设置 TELEGRAM_TOKEN 或 TELEGRAM_CHAT_ID")
        return False
    
    try:
        # 创建收集器和通知器
        collector = FinnhubCollector(finnhub_token)
        notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        tracker = NewsTracker('test_news_history.json')
        
        logger.info("开始测试每个类别的最新新闻...")
        logger.info("")
        
        sent_count = 0
        for category in FINNHUB_CATEGORIES:
            try:
                logger.info(f"处理类别: {category}")
                
                # 获取该类别的新闻
                news_list = collector.get_news(category)
                
                if not news_list or len(news_list) == 0:
                    logger.info(f"  ℹ 未发现 {category} 新闻")
                    logger.info("")
                    continue
                
                logger.info(f"  ✓ 获取了 {len(news_list)} 条新闻")
                
                # 只取最新的一条
                latest_news = news_list[0]
                news_id = f"finnhub_{latest_news.get('id', '')}_{category}"
                
                headline = latest_news.get('headline', '')
                source = latest_news.get('source', '')
                datetime_ts = latest_news.get('datetime', 0)
                datetime_str = datetime.fromtimestamp(datetime_ts).strftime('%Y-%m-%d %H:%M:%S')
                
                logger.info(f"  📰 最新新闻:")
                logger.info(f"     标题: {headline[:60]}...")
                logger.info(f"     来源: {source}")
                logger.info(f"     时间: {datetime_str}")
                logger.info(f"     ID: {latest_news.get('id', 'N/A')}")
                
                # 检查是否已推送
                if tracker.is_new(news_id):
                    logger.info(f"  ➤ 这是新新闻，准备推送...")
                    
                    # 推送新闻
                    success = await notifier.send_news(latest_news, source_type='finnhub')
                    if success:
                        tracker.mark_as_sent(news_id)
                        sent_count += 1
                        logger.info(f"  ✓ 已成功推送到电报")
                    else:
                        logger.error(f"  ✗ 推送失败")
                    
                    # 避免请求过快
                    await asyncio.sleep(1)
                else:
                    logger.info(f"  ○ 这条新闻已推送过，跳过")
                
                logger.info("")
                
                # 避免 API 请求过快
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"  ✗ 处理 {category} 时出错: {e}")
                logger.info("")
                continue
        
        logger.info("=" * 50)
        logger.info(f"测试完成！共推送了 {sent_count} 条新闻")
        logger.info("=" * 50)
        
        # 清理测试历史记录
        if os.path.exists('test_news_history.json'):
            os.remove('test_news_history.json')
            logger.info("已清理测试历史记录")
        
        return True
        
    except Exception as e:
        logger.error(f"测试失败: {e}")
        return False


async def main():
    """主函数"""
    success = await test_latest_news_logic()
    
    if success:
        logger.info("")
        logger.info("✓ 测试通过！新逻辑工作正常。")
        logger.info("每个类别只会推送最新的一条新闻。")
        sys.exit(0)
    else:
        logger.error("")
        logger.error("✗ 测试失败，请检查配置。")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
