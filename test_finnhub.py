#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Finnhub API 测试脚本
"""

from dotenv import load_dotenv
load_dotenv()

import os
import sys
import logging
import requests
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

FINNHUB_CATEGORIES = ['general', 'forex', 'crypto', 'merger']

def test_finnhub(token: str):
    """测试 Finnhub API"""
    logger.info("=" * 50)
    logger.info("测试 Finnhub API")
    logger.info("=" * 50)
    
    try:
        base_url = 'https://finnhub.io/api/v1'
        
        total_news = 0
        for category in FINNHUB_CATEGORIES:
            try:
                logger.info(f"测试类别: {category}")
                
                url = f"{base_url}/news"
                params = {
                    'category': category,
                    'token': token
                }
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                news_list = response.json()
                
                if isinstance(news_list, list) and len(news_list) > 0:
                    count = len(news_list)
                    total_news += count
                    logger.info(f"  ✓ {category}: 获取了 {count} 条新闻")
                    
                    # 显示第一条新闻
                    first_news = news_list[0]
                    logger.info(f"    标题: {first_news.get('headline', 'N/A')}")
                    logger.info(f"    来源: {first_news.get('source', 'N/A')}")
                    datetime_str = datetime.fromtimestamp(first_news.get('datetime', 0)).strftime('%Y-%m-%d %H:%M:%S')
                    logger.info(f"    时间: {datetime_str}")
                else:
                    logger.info(f"  ℹ {category}: 未获取到新闻")
                    
            except Exception as e:
                logger.error(f"  ✗ {category}: 获取失败 - {e}")
        
        logger.info(f"总共获取了 {total_news} 条新闻")
        logger.info("✓ Finnhub API 测试成功")
        return True
        
    except Exception as e:
        logger.error(f"✗ Finnhub API 测试失败: {e}")
        return False


def main():
    """主测试函数"""
    logger.info("Finnhub API 测试套件")
    logger.info("=" * 50)
    
    # 从环境变量读取配置
    finnhub_token = os.getenv('FINNHUB_TOKEN')
    
    # 验证配置
    if not finnhub_token:
        logger.error("未设置 FINNHUB_TOKEN 环境变量")
        sys.exit(1)
    
    logger.info(f"Finnhub Token: {finnhub_token[:10]}...")
    logger.info("=" * 50)
    
    # 运行测试
    success = test_finnhub(finnhub_token)
    
    logger.info("=" * 50)
    
    if success:
        logger.info("✓ 测试通过！Finnhub API 已准备好使用。")
        sys.exit(0)
    else:
        logger.error("✗ 测试失败，请检查配置。")
        sys.exit(1)


if __name__ == '__main__':
    main()
