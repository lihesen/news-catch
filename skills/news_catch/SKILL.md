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

# 【最佳实践】抓取最近 12 小时的全部新闻，而不是用 category 过滤
sina_news = client.get_sina_finance_news(hours=12)
zaobao_news = client.get_zaobao_news(hours=12)

print(f"Fetched {len(sina_news)} items from the last 12 hours.")
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

1. **组合时间过滤进行 AI 深度判定**: 对于用户提出的抽象或复杂的行业分类要求（比如“关于新能源汽车的利空消息”），**切忌将整段话塞给 `category`**. 你必须使用 `hours` 参数拉回全量新闻后，将 `[{"title": "..."}]` 的 JSON 数据塞给你自己的大语言模型系统，让你的 AI 引擎去判定和提纯。
2. **容错处理**: 如果返回为空列表 `[]`，可能是设定时间段内真的没有新闻，可以直接反馈给用户，不要捏造内容。
