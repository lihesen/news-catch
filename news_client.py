import requests
from bs4 import BeautifulSoup
import urllib.parse

class NewsClient:
    """
    新闻抓取客户端，提供获取新浪财经7x24与联合早报即时新闻的方法。
    """
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }

    def get_sina_finance_news(self, limit=20, category=None) -> list:
        """
        获取新浪财经 7x24 小时新闻快讯
        :param limit: 返回的最大条数
        :param category: 可选的分类/关键词过滤 (例如 'A股', '美股', '宏观')
        """
        # 如果有分类过滤，我们需要获取更多的数据以供筛选
        fetch_size = limit * 5 if category else limit
        url = f"https://zhibo.sina.com.cn/api/zhibo/feed?callback=&page=1&page_size={fetch_size}&zhibo_id=152"
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
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
                    
                create_time = item.get('create_time', '')
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
            print(f"Error fetching Sina Finance: {e}")
            
        return results

    def get_zaobao_news(self, limit=20, category=None) -> list:
        """
        获取新加坡联合早报 即时新闻
        :param limit: 返回的最大条数
        :param category: 可选的分类/关键词过滤 (例如 'A股', '美股', '宏观', '科技')
        """
        base_url = "https://www.zaobao.com"
        url = f"{base_url}/realtime"
        results = []
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 使用 .card 选择器查找文章列表
            cards = soup.select('.card')
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
                    "time": time_str,
                    "url": link
                })
        except Exception as e:
            print(f"Error fetching Lianhe Zaobao: {e}")
            
        return results
