from news_client import NewsClient
import json

def main():
    client = NewsClient()
    
    print("Fetching Sina Finance News (A股)...")
    sina_news = client.get_sina_finance_news(limit=3, category="A股")
    print(json.dumps(sina_news, indent=2, ensure_ascii=False))
    
    print("\n" + "="*50 + "\n")
    
    print("Fetching Lianhe Zaobao News (科技)...")
    zaobao_news = client.get_zaobao_news(limit=3, category="科技")
    print(json.dumps(zaobao_news, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
