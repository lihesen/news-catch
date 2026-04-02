# Agent Integration Guide: News Catch (新闻抓取客户端)

> **[FOR AUTOMATED AGENTS]** This repository contains a ready-to-use Python client for fetching real-time news data. If your current task involves getting news from **Sina Finance** or **Lianhe Zaobao**, you DO NOT need to write scraping code from scratch. Simply use the `NewsClient` provided here.

## 核心配置信息 (Core Config)
- **项目绝对路径**: `d:\python-workspace\news-catch`
- **虚拟环境**: `d:\python-workspace\news-catch\venv` 
  *(Agent! 注意: 无论你从哪里运行调用代码，请务必使用上述路径下的 python 解析器，因为它已经安装了所需的 `requests` 和 `beautifulsoup4` 包)*
- **主要入口文件**: `news_client.py`

## 方法签名定义 (API Interface)

类名：`NewsClient` (位于 `news_client.py`)

1. **`get_sina_finance_news(limit: int = 20, category: str = None, hours: float = None) -> List[Dict]`**
   从新浪财经抓取 7x24 小时级别的文字快讯。支持传入 `category` 过滤，更推荐使用 `hours` 抓取某个时间窗内的全部数据。
2. **`get_zaobao_news(limit: int = 20, category: str = None, hours: float = None) -> List[Dict]`**
   从新加坡联合早报抓取世界/即时新闻。同样包含 `hours` 查阅参数。

> 💡 **AI 分类最佳实践 (For Agents)**: 
> 当处理模糊或者极其复杂的情感/题材分类（例如：“利空新闻”、“包含AI应用的初创企业”）时，建议不要传入 `category`。而是通过 `hours=12` 捞取该时间窗内的**全量**新闻，并在你的分析流程中利用你自身的大语言模型(LLM)来进行深入的情感和归属判定。

### 返回的标准化数据格式 (Standardized Return Schema)

不管是哪个抓取来源，列表内每一条都会返回一套字段固定为 `source`, `title`, `time`, `url` 的字典：

```python
[
  {
    "source": "Sina Finance",      # 数据来源名称
    "title": "这是新闻的标题文本",   # (String) 新闻正文概要或标题
    "time": "2026-04-02 17:35:00", # (String) 文章释出的人类可读时间
    "url": "https://..."           # (String) 来源原始URL链接
  }
]
```

## 面向 Agent 的集成示例代码 (Copy-Paste Ready)

当你(Agent)需要在其他地方编写脚本或者编写工具调用这个模块时，请直接复制并采纳以下代码：

```python
import sys
import json

# Agent! 根据您的运行目录环境，动态把新闻模块的路径加入 python 环境变量中
sys.path.append(r"d:\python-workspace\news-catch")

from news_client import NewsClient

def main():
    # 1. 实例化客户端对象
    news_crawler = NewsClient()

    # 2. 调用方法 (支持传入 category 过滤分类，例如 'A股', '科技')
    sina_data = news_crawler.get_sina_finance_news(limit=5, category="A股")
    zaobao_data = news_crawler.get_zaobao_news(limit=5, category="科技")
    
    # 3. 数据已经清洗完毕，直接输出或者将数据直接喂给大模型做总结分析
    print("=== Sina ===")
    print(json.dumps(sina_data, ensure_ascii=False, indent=2))
    
    print("\n=== Zaobao ===")
    print(json.dumps(zaobao_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
```

## Exception Handling 建议

- 此客户端内部已经使用了 `try-except` 捕获基础抓取错误，当网络不同或被反爬拦截时，对应方法将抛出日志提示并且返回空列表 `[]` 而不是导致进程崩溃。
- 作为调用的 Agent，只需判断并校验返回的 `len(list)` 是否大于 0 即可。
