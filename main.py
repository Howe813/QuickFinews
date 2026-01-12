#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QuickFinews - 财经新闻实时推送机器人
集成 TuShare 新闻接口、Finnhub API 和电报机器人
"""

from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

import os
import sys
import time
import logging
import threading
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
import requests
import tushare as ts
from telegram import Bot
from telegram.error import TelegramError
import asyncio

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quickfinews.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# TuShare 新闻来源列表
TUSHARE_SOURCES = ['sina', 'wallstreetcn', '10jqka', 'eastmoney', 'yuncaijing', 'fenghuang', 'jinrongjie', 'cls', 'yicai']

# Finnhub 新闻类别
FINNHUB_CATEGORIES = ['general', 'forex', 'crypto', 'merger']

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
    'yicai': '第一财经',
    'finnhub_general': 'Finnhub 综合新闻',
    'finnhub_forex': 'Finnhub 外汇新闻',
    'finnhub_crypto': 'Finnhub 加密货币',
    'finnhub_merger': 'Finnhub 并购新闻'
}


class NewsTracker:
    """新闻追踪器 - 记录已推送的新闻，避免重复"""
    
    def __init__(self, history_file: str = 'news_history.json'):
        self.history_file = history_file
        self.news_ids: Set[str] = set()
        self.load_history()
    
    def load_history(self):
        """从文件加载历史记录"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.news_ids = set(data.get('ids', []))
                    logger.info(f"加载了 {len(self.news_ids)} 条历史新闻记录")
            except Exception as e:
                logger.error(f"加载历史记录失败: {e}")
                self.news_ids = set()
    
    def save_history(self):
        """保存历史记录到文件"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump({'ids': list(self.news_ids)}, f, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存历史记录失败: {e}")
    
    def is_new(self, news_id: str) -> bool:
        """检查新闻是否已推送过"""
        return news_id not in self.news_ids
    
    def mark_as_sent(self, news_id: str):
        """标记新闻为已推送"""
        self.news_ids.add(news_id)
        self.save_history()


class TelegramNotifier:
    """电报通知器"""
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.bot = Bot(token=token)
    
    async def send_message(self, text: str) -> bool:
        """发送消息到电报"""
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=text,
                parse_mode='HTML'
            )
            logger.info(f"消息已发送到电报 (Chat ID: {self.chat_id})")
            return True
        except TelegramError as e:
            logger.error(f"发送电报消息失败: {e}")
            return False
    
    async def send_news(self, news: Dict, source_type: str = 'tushare') -> bool:
        """发送新闻到电报"""
        try:
            if source_type == 'tushare':
                # TuShare 新闻格式
                source = SOURCE_NAMES.get(news.get('src', ''), news.get('src', ''))
                title = news.get('title', '无标题')
                content = news.get('content', '')
                datetime_str = news.get('datetime', '')
                
                # 限制内容长度
                if len(content) > 200:
                    content = content[:200] + "..."
                
                message = f"""
<b>📰 {source}</b>
<b>{title}</b>

{content}

<i>{datetime_str}</i>
"""
            else:
                # Finnhub 新闻格式
                source = SOURCE_NAMES.get(news.get('source_key', ''), 'Finnhub')
                headline = news.get('headline', '无标题')
                summary = news.get('summary', '')
                url = news.get('url', '')
                datetime_ts = news.get('datetime', 0)
                datetime_str = datetime.fromtimestamp(datetime_ts).strftime('%Y-%m-%d %H:%M:%S')
                
                # 清理 HTML 标签
                import re
                summary = re.sub(r'<[^>]+>', '', summary)
                headline = re.sub(r'<[^>]+>', '', headline)
                
                # 限制摘要长度
                if len(summary) > 200:
                    summary = summary[:200] + "..."
                
                message = f"""
<b>🌐 {source}</b>
<b>{headline}</b>

{summary}

<a href="{url}">阅读原文</a>

<i>{datetime_str}</i>
"""
            
            await self.send_message(message)
            return True
        except Exception as e:
            logger.error(f"发送新闻失败: {e}")
            return False


class TuShareCollector:
    """TuShare 新闻收集器"""
    
    def __init__(self, tushare_token: str):
        ts.set_token(tushare_token)
        self.pro = ts.pro_api()
    
    def get_news(self, src: str, start_date: str, end_date: str) -> List[Dict]:
        """获取指定来源的新闻"""
        try:
            df = self.pro.news(src=src, start_date=start_date, end_date=end_date)
            if df is None or df.empty:
                return []
            
            # 转换为字典列表
            news_list = df.to_dict('records')
            for news in news_list:
                news['src'] = src
            logger.info(f"从 {SOURCE_NAMES.get(src, src)} 获取了 {len(news_list)} 条新闻")
            return news_list
        except Exception as e:
            logger.error(f"获取 {src} 新闻失败: {e}")
            return []
    
    def get_all_news(self, start_date: str, end_date: str) -> List[Dict]:
        """获取所有来源的新闻"""
        all_news = []
        for source in TUSHARE_SOURCES:
            news = self.get_news(source, start_date, end_date)
            all_news.extend(news)
            # 避免请求过快
            time.sleep(1)
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('datetime', ''), reverse=True)
        return all_news


class FinnhubCollector:
    """Finnhub 新闻收集器"""
    
    def __init__(self, finnhub_token: str):
        self.token = finnhub_token
        self.base_url = 'https://finnhub.io/api/v1'
        self.last_check_times = {}  # 记录每个类别的最后检查时间
    
    def get_news(self, category: str = 'general', min_id: int = 0) -> List[Dict]:
        """获取指定类别的新闻"""
        try:
            url = f"{self.base_url}/news"
            params = {
                'category': category,
                'token': self.token
            }
            
            if min_id > 0:
                params['minId'] = min_id
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_list = response.json()
            
            if not isinstance(news_list, list):
                logger.error(f"Finnhub API 返回格式错误: {news_list}")
                return []
            
            # 添加来源标识
            for news in news_list:
                news['source_key'] = f'finnhub_{category}'
                news['category_name'] = category
            
            logger.info(f"从 Finnhub {category} 获取了 {len(news_list)} 条新闻")
            return news_list
            
        except requests.exceptions.RequestException as e:
            logger.error(f"获取 Finnhub {category} 新闻失败: {e}")
            return []
        except Exception as e:
            logger.error(f"处理 Finnhub {category} 新闻失败: {e}")
            return []
    
    def get_all_news(self, categories: List[str] = None) -> List[Dict]:
        """获取所有类别的新闻"""
        if categories is None:
            categories = FINNHUB_CATEGORIES
        
        all_news = []
        for category in categories:
            news = self.get_news(category)
            all_news.extend(news)
            # 避免请求过快
            time.sleep(0.5)
        
        # 按时间排序
        all_news.sort(key=lambda x: x.get('datetime', 0), reverse=True)
        return all_news


class NewsBot:
    """新闻机器人 - 主控制器"""
    
    def __init__(self, tushare_token: str, finnhub_token: str, telegram_token: str, telegram_chat_id: str):
        self.tushare_collector = TuShareCollector(tushare_token) if tushare_token else None
        self.finnhub_collector = FinnhubCollector(finnhub_token) if finnhub_token else None
        self.notifier = TelegramNotifier(telegram_token, telegram_chat_id)
        self.tracker = NewsTracker()
        self.running = False
        self.last_check_time = datetime.now() - timedelta(minutes=5)
        self.last_finnhub_ids = {}  # 记录每个类别的最后新闻ID
    
    async def check_and_push_tushare_news(self):
        """检查并推送 TuShare 新闻"""
        if not self.tushare_collector:
            return
        
        try:
            # 计算时间范围（最近5分钟）
            end_time = datetime.now()
            start_time = self.last_check_time
            
            start_date = start_time.strftime('%Y-%m-%d %H:%M:%S')
            end_date = end_time.strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"检查 TuShare 新闻: {start_date} 到 {end_date}")
            
            # 获取新闻
            news_list = self.tushare_collector.get_all_news(start_date, end_date)
            
            if not news_list:
                logger.info("未发现 TuShare 新闻")
                return
            
            logger.info(f"发现 {len(news_list)} 条 TuShare 新闻")
            
            # 推送新新闻
            sent_count = 0
            for news in news_list:
                # 生成唯一ID
                news_id = f"tushare_{news.get('src', '')}_{news.get('datetime', '')}_{hash(news.get('title', ''))}"
                
                if self.tracker.is_new(news_id):
                    # 推送新闻
                    success = await self.notifier.send_news(news, source_type='tushare')
                    if success:
                        self.tracker.mark_as_sent(news_id)
                        sent_count += 1
                    # 避免请求过快
                    await asyncio.sleep(0.5)
            
            logger.info(f"本次推送了 {sent_count} 条 TuShare 新闻")
            
        except Exception as e:
            logger.error(f"检查和推送 TuShare 新闻时出错: {e}")
    
    async def check_and_push_finnhub_news(self):
        """检查并推送 Finnhub 新闻（每个类别只推送最新一条）"""
        if not self.finnhub_collector:
            return
        
        try:
            logger.info("检查 Finnhub 新闻")
            
            # 按类别分别获取新闻
            sent_count = 0
            for category in FINNHUB_CATEGORIES:
                try:
                    # 获取该类别的新闻
                    news_list = self.finnhub_collector.get_news(category)
                    
                    if not news_list or len(news_list) == 0:
                        logger.info(f"未发现 Finnhub {category} 新闻")
                        continue
                    
                    # 只取最新的一条（按时间排序，第一条就是最新的）
                    latest_news = news_list[0]
                    news_id = f"finnhub_{latest_news.get('id', '')}_{category}"
                    
                    # 检查是否已推送
                    if self.tracker.is_new(news_id):
                        logger.info(f"Finnhub {category} 有新新闻: {latest_news.get('headline', '')[:50]}...")
                        
                        # 推送新闻
                        success = await self.notifier.send_news(latest_news, source_type='finnhub')
                        if success:
                            self.tracker.mark_as_sent(news_id)
                            sent_count += 1
                            logger.info(f"✓ 已推送 Finnhub {category} 最新新闻")
                        
                        # 避免请求过快
                        await asyncio.sleep(0.5)
                    else:
                        logger.debug(f"Finnhub {category} 最新新闻已推送过")
                    
                    # 避免 API 请求过快
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"处理 Finnhub {category} 新闻时出错: {e}")
                    continue
            
            if sent_count > 0:
                logger.info(f"本次推送了 {sent_count} 条 Finnhub 新闻")
            else:
                logger.info("没有新的 Finnhub 新闻需要推送")
            
        except Exception as e:
            logger.error(f"检查和推送 Finnhub 新闻时出错: {e}")
    
    async def check_and_push_news(self):
        """检查并推送所有新闻"""
        # 检查 TuShare 新闻
        await self.check_and_push_tushare_news()
        
        # 检查 Finnhub 新闻
        await self.check_and_push_finnhub_news()
        
        # 更新最后检查时间
        self.last_check_time = datetime.now()
    
    async def run(self, check_interval: int = 60):
        """运行机器人"""
        self.running = True
        logger.info(f"新闻机器人启动，检查间隔: {check_interval} 秒")
        
        try:
            while self.running:
                await self.check_and_push_news()
                await asyncio.sleep(check_interval)
        except KeyboardInterrupt:
            logger.info("收到停止信号，正在关闭...")
            self.running = False
        except Exception as e:
            logger.error(f"机器人运行出错: {e}")
            self.running = False
    
    def stop(self):
        """停止机器人"""
        self.running = False
        logger.info("机器人已停止")


async def main():
    """主函数"""
    # 从环境变量读取配置
    tushare_token = os.getenv('TUSHARE_TOKEN')
    finnhub_token = os.getenv('FINNHUB_TOKEN')
    telegram_token = os.getenv('TELEGRAM_TOKEN')
    telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    check_interval = int(os.getenv('CHECK_INTERVAL', '60'))
    
    # 验证配置
    if not telegram_token:
        logger.error("未设置 TELEGRAM_TOKEN 环境变量")
        sys.exit(1)
    
    if not telegram_chat_id:
        logger.error("未设置 TELEGRAM_CHAT_ID 环境变量")
        sys.exit(1)
    
    if not tushare_token and not finnhub_token:
        logger.error("至少需要设置 TUSHARE_TOKEN 或 FINNHUB_TOKEN 中的一个")
        sys.exit(1)
    
    logger.info("=" * 50)
    logger.info("QuickFinews - 财经新闻实时推送机器人")
    logger.info("=" * 50)
    
    if tushare_token:
        logger.info(f"TuShare Token: {tushare_token[:10]}...")
    else:
        logger.info("TuShare: 未启用")
    
    if finnhub_token:
        logger.info(f"Finnhub Token: {finnhub_token[:10]}...")
    else:
        logger.info("Finnhub: 未启用")
    
    logger.info(f"Telegram Chat ID: {telegram_chat_id}")
    logger.info(f"检查间隔: {check_interval} 秒")
    logger.info("=" * 50)
    
    # 创建机器人
    bot = NewsBot(tushare_token, finnhub_token, telegram_token, telegram_chat_id)
    
    # 运行机器人
    try:
        await bot.run(check_interval=check_interval)
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭...")
        bot.stop()


if __name__ == '__main__':
    asyncio.run(main())
