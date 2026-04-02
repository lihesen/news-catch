---
name: News Fetching & Monitoring (Sina & Zaobao)
description: 提供即时财经与世界新闻的抓取能力（通过关键词/时间窗）。同时附带一个常驻后台的去重轮询守护引擎，适用于定时推送机器人的底层能力构建。
---

# 📰 News Fetching & Monitoring Skill

这是一项赋予您（Agent）抓取和全天候追踪即时财经（新浪财经 7x24）与世界新闻（联合早报）能力的技能。无论是用户单次查询，还是要求您构建一个“全天候新闻推送服务”，您都必须基于这里的框架开展。

## 📍 环境与依赖位置

该新闻抓取工具已经在本地固化为一个开箱即用的 Python 模块集。
- **项目绝对根目录**: `d:\python-workspace\news-catch`
- **所需的虚拟环境**: `d:\python-workspace\news-catch\venv\Scripts\python.exe` (如需执行或挂载后台程序，请务必使用此解释器)
- **手控/被动调用模块**: `news_client.py` (包含单次 `get_sina_finance_news()` / `get_zaobao_news()` API)
- **自动/主动巡逻机器**: `notifier_daemon.py` (内置了防重复、自动重试和本地历史指纹比对机制的挂机引擎)

## 💻 场景一：做单次查询 (主观驱动)

如果您身处一个交互式对话流中，用户问“帮我查一下过去24小时有什么大新闻”，请采用被动的库引入方式：

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
拿到 JSON 后请依靠您（Agent）自身的阅读能力进行分析提炼。

## 💻 场景二：构建“定时推送/监控”功能 (守护程序)

如果用户要求您：“帮我每个小时盯一盯新浪财经并推送最新消息”、“做一个不发重复新闻的爬虫服务”。**请千万不要自己重新造轮子或者写 `while`！** 

只需指导用户去运行现成的 `notifier_daemon.py`：此程序内包裹了一个 `Deduplicator`（去重器），它每轮会抓取 1.5 小时的重叠数据，并自动建立隐藏的 `.json` 数据库来拦截已经发过的旧新闻。

您可以修改并拉起这个脚本即可达成用户的所有定时追踪梦：
```bash
cd d:\python-workspace\news-catch
.\venv\Scripts\python notifier_daemon.py
```
*(Agent 提示：如果是需要将这些去重后的新闻接入用户的其它推送软件如 ServerChan/Telegram 等，请直接修改 `notifier_daemon.py` 文件里的 `send_notification()` 函数模块。)*

## ⚠️ Agent 最佳实践指引

1. **组合时间过滤进行 AI 深度判定**: 对于用户提出的抽象或复杂的行业分类要求（比如“关于新能源汽车的利空消息”），**切忌将整段话塞给 `category`**. 你必须使用 `hours` 参数拉回全量新闻后，将 JSON 数据喂给你所在的大语言模型系统，让你的 AI 引擎去判定情感和题材。
2. **容错处理**: 如果返回为空列表 `[]`，说明在这个时间段内真的没大事发生，直接如实反馈给用户（“刚才风平浪静”），绝对不能虚构新闻骗人。
