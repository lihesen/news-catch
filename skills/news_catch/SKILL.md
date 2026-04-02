---
name: News Fetching (Sina & Zaobao)
description: 获取最新的新浪财经 7x24 小时快讯以及新加坡联合早报即时新闻，支持按 A股/港股/美股/宏观/科技 等分类过滤。
---

# 📰 News Fetching Skill

这是一项赋予您（Agent）抓取和获取即时财经/世界新闻能力的技能。当用户要求追踪股市动态、查询最新宏观经济新闻、分析突发事件时，您必须使用此技能中提供的客户端接口。

## 📍 环境与依赖位置

该新闻抓取工具已经在本地固化为一个开箱即用的 Python 模块。
- **项目绝对根目录**: `d:\python-workspace\news-catch`
- **所需的虚拟环境**: `d:\python-workspace\news-catch\venv\Scripts\python.exe` (如需在终端执行脚本，请务必使用此解释器)
- **核心模块**: `news_client.py`

## 💻 如何调用 (Python Code)

当需要查询新闻时，请在您的 Python 脚本或交互环境中添加以下代码。这里展示了如何将路径加入 `sys.path` 以便随时随地 import：

```python
import sys
import json
sys.path.append(r"d:\python-workspace\news-catch")
from news_client import NewsClient

client = NewsClient()

# 1. 提取带关键词过滤的新浪财经新闻 (例如：A股, 宏观)
# 如果不需要过滤，请去掉 category 参数
sina_news = client.get_sina_finance_news(limit=10, category="A股")

# 2. 提取新加坡联合早报的大事追踪
zaobao_news = client.get_zaobao_news(limit=10, category="科技")

print(json.dumps(sina_news, ensure_ascii=False, indent=2))
```

## 📊 数据返回结构

无论调用哪个方法，返回的都是一个 `List[Dict]`，您可以直接将这个列表当做 observation context 交给大模型进行阅读理解和提炼。

```json
[
  {
    "source": "Sina Finance",
    "title": "具体的新闻标题或快讯正文",
    "time": "2026-04-02 17:35:00",
    "url": "https://..."
  }
]
```

## ⚠️ 最佳实践指引

1. **组合过滤**: 如果用户只需要“美股”新闻，请不要获取所有新闻后再由您大模型强行处理，而是直接在调用函数时加上 `category="美股"`，这样更节省上下文且精确。
2. **容错处理**: 如果返回为空列表 `[]`，可能是因为暂时没有包含该关键词的新闻，告知用户不要强行捏造内容。
