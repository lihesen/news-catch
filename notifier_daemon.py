import json
import os
import time
from datetime import datetime
import hashlib
from news_client import NewsClient
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NotifierDaemon")

SEEN_FILE = "seen_news.json"
MAX_SEEN_ITEMS = 5000  # 防止指纹记录文件无限膨胀

class Deduplicator:
    def __init__(self):
        self.seen_hashes = self._load()

    def _load(self):
        if os.path.exists(SEEN_FILE):
            try:
                with open(SEEN_FILE, "r", encoding="utf-8") as f:
                    return set(json.load(f))
            except Exception as e:
                logger.warning(f"本地缓存已损坏，正在重置: {e}")
                return set()
        return set()

    def _save(self):
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            # 只保留最新的 MAX_SEEN_ITEMS 个，防止文件无限膨胀
            json.dump(list(self.seen_hashes)[-MAX_SEEN_ITEMS:], f)

    def _compute_hash(self, news_item):
        """
        组合标题和来源来生成唯一标识符 (URL有时可能变动或者不可靠)
        """
        raw = f"{news_item['source']}_{news_item['title']}_{news_item['time']}"
        return hashlib.md5(raw.encode('utf-8')).hexdigest()

    def filter_new(self, news_list):
        new_items = []
        for item in news_list:
            item_hash = self._compute_hash(item)
            if item_hash not in self.seen_hashes:
                self.seen_hashes.add(item_hash)
                new_items.append(item)
        
        if new_items:
            self._save()
        return new_items


def send_notification(news_item):
    """
    具体的推送渠道逻辑。
    目前为打印到控制台。如果您需要接入微信、钉钉或企业微信，在这里编写 requests POST 逻辑即可。
    """
    logger.info(f"🚀 [NEW] {news_item['source']} | {news_item['time']} | {news_item['title']}")
    # print(json.dumps(news_item, indent=2, ensure_ascii=False))


def job_fetch_and_notify():
    client = NewsClient()
    dedup = Deduplicator()
    
    logger.info("开始拉取并比对最新新闻...")
    
    # 故意扩大单次拉取时间窗（比如原定每 1 小时查一次，这里输入 1.5），制造重叠区
    FETCH_HOURS_OVERLAP = 1.5 
    
    # 1. 拉取所有数据
    sina_news = client.get_sina_finance_news(hours=FETCH_HOURS_OVERLAP)
    zaobao_news = client.get_zaobao_news(hours=FETCH_HOURS_OVERLAP)
    
    all_news = sina_news + zaobao_news
    
    # 因为抓回来的是从新到旧的，推送时如果是多条，建议按照从旧到新的时间顺序推送
    # 对其进行翻转排序
    all_news.reverse()
    
    # 2. 本地指纹去重比对
    new_items = dedup.filter_new(all_news)
    
    logger.info(f"共拉取到 {len(all_news)} 条数据，经过指纹比对后，发现全新未推送内容 {len(new_items)} 条。")
    
    # 3. 发送推送（仅发送新的）
    for item in new_items:
        send_notification(item)


if __name__ == "__main__":
    # ==========================
    # 模式选择：
    # 如果想交给 Windows/Linux 定时任务处理，仅需单次运行：
    # job_fetch_and_notify()
    # 
    # 如果想直接在后台死循环持久运行（每小时执行一次）：
    # ==========================
    FETCH_INTERVAL_SECONDS = 3600
    
    logger.info(f"启动自动监听模式，每 {FETCH_INTERVAL_SECONDS} 秒扫描一次以防遗漏...")
    
    # 刚启动时可以先跑一下弥补启动前的空白
    job_fetch_and_notify()
    
    while True:
        time.sleep(FETCH_INTERVAL_SECONDS)
        try:
            job_fetch_and_notify()
        except Exception as e:
            logger.error(f"自动化扫描遇到不可预期的错误: {e}")
