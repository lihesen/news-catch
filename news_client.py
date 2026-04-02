import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import urllib.parse
from datetime import datetime, timedelta
import logging
import re

# 配置 Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("NewsClient")

class NewsClient:
    """
    新闻抓取客户端，提供获取新浪财经7x24与联合早报即时新闻的方法。
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        
        # 配置带有自动重试机制的 Session
        self.session = requests.Session()
        retry = Retry(
            total=3,          # 自动重试 3 次
            read=3,
            connect=3,
            backoff_factor=0.3, # 退避系数
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

    def _normalize_time(self, time_str: str) -> str:
        """
        统一时间格式为 YYYY-MM-DD HH:MM:SS
        """
        if not time_str:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        time_str = time_str.strip()
        
        # 已经是标准格式
        if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', time_str):
            return time_str
            
        now = datetime.now()
        
        # 相对时间处理
        if "分钟前" in time_str:
            m = re.search(r'\d+', time_str)
            if m: return (now - timedelta(minutes=int(m.group()))).strftime("%Y-%m-%d %H:%M:%S")
        elif "小时前" in time_str:
            m = re.search(r'\d+', time_str)
            if m: return (now - timedelta(hours=int(m.group()))).strftime("%Y-%m-%d %H:%M:%S")
        elif "天前" in time_str:
            m = re.search(r'\d+', time_str)
            if m: return (now - timedelta(days=int(m.group()))).strftime("%Y-%m-%d %H:%M:%S")
        elif "昨天" in time_str:
            m = re.search(r'(\d{2}):(\d{2})', time_str)
            t = now - timedelta(days=1)
            return t.strftime(f"%Y-%m-%d {m.group(1)}:{m.group(2)}:00") if m else t.strftime("%Y-%m-%d %H:%M:%S")
            
        # 提取 "4月2日 17:35" 或者类似格式
        match = re.search(r'(\d{1,2})[-/月](\d{1,2})[-/日]?\s*(\d{1,2}):(\d{1,2})', time_str)
        if match:
            month, day, hour, minute = map(int, match.groups())
            return f"{now.year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:00"
            
        return time_str

    def get_sina_finance_news(self, limit=20, category=None) -> list:
        """
        获取新浪财经 7x24 小时新闻快讯
        :param limit: 返回的最大条数
        :param category: 可选的分类/关键词过滤 (例如 'A股', '美股', '宏观')
        """
        # 如果有分类过滤，我们需要获取更多的近期数据从中筛选（抓取最近 200 条）
        fetch_size = max(limit * 20, 200) if category else limit
        url = f"https://zhibo.sina.com.cn/api/zhibo/feed?callback=&page=1&page_size={fetch_size}&zhibo_id=152"
        results = []
        try:
            response = self.session.get(url, headers=self.headers, timeout=10)
            data = response.json()
            
            # 兼容可能的数据结构
            if 'data' in data.get('result', {}):
                items = data['result']['data'].get('feed', {}).get('list', [])
            else:
                items = []

            for item in items:
                title = item.get('rich_text', '')
                if not title:
                    title = item.get('content', '')
                    
                if category and category.lower() not in title.lower():
                    continue
                    
                create_time = self._normalize_time(item.get('create_time', ''))
                docurl = item.get('docurl', '')
                results.append({
                    "source": "Sina Finance",
                    "title": title,
                    "time": create_time,
                    "url": docurl
                })
                
                if len(results) >= limit:
                    break
        except Exception as e:
            logger.error(f"Error fetching Sina Finance: {e}")
            
        return results

    def get_zaobao_news(self, limit=20, category=None) -> list:
        """
        获取新加坡联合早报 即时新闻
        :param limit: 返回的最大条数
        :param category: 可选的分类/关键词过滤 (例如 'A股', '美股', '宏观', '科技')
        """
        base_url = "https://www.zaobao.com"
        results = []
        max_pages = 5 if category else 1
        
        try:
            for page in range(0, max_pages):
                if len(results) >= limit:
                    break
                    
                url = f"{base_url}/realtime?page={page}"
                response = self.session.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 使用 .card 选择器查找文章列表
                cards = soup.select('.card')
                if not cards:
                    break # No more content
                    
                for card in cards:
                    if len(results) >= limit:
                        break
                    
                    a_tag = card.find('a', href=True)
                    if not a_tag:
                        continue
                    
                    link = a_tag['href']
                    if not link.startswith('http'):
                        link = urllib.parse.urljoin(base_url, link)
                    
                    # 寻找标题，一般在 h2 等 class 里包含 content 或者 title 等
                    title_tag = card.find(['h2', 'h3', 'h4', 'div'], class_=lambda x: x and ('title' in x.lower() or 'content' in x.lower()))
                    if title_tag:
                        title = title_tag.get_text(strip=True)
                    else:
                        title = a_tag.get_text(strip=True)
                    
                    if not title:
                        continue
                        
                    if category and category.lower() not in title.lower():
                        continue
                    
                    # 时间
                    time_div = card.find('div', class_=lambda x: x and 'timestamp' in x.lower())
                    time_str = time_div.get_text(strip=True) if time_div else ''
                        
                    results.append({
                        "source": "Lianhe Zaobao",
                        "title": title,
                        "time": self._normalize_time(time_str),
                        "url": link
                    })
        except Exception as e:
            logger.error(f"Error fetching Lianhe Zaobao: {e}")
            
        return results
