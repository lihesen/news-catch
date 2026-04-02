from news_client import NewsClient
import json

def main():
    client = NewsClient()
    
    print("Fetching Sina Finance News (A股, past 12 hours)...")
    sina_news = client.get_sina_finance_news(category="A股", hours=12)
    print(json.dumps(sina_news[:3], indent=2, ensure_ascii=False))
    print(f"Total entries fetched in the past 12 hours: {len(sina_news)}")
    
    print("\n" + "="*50 + "\n")
    
    print("Fetching Lianhe Zaobao News (Past 2 hours)...")
    zaobao_news = client.get_zaobao_news(hours=2)
    print(json.dumps(zaobao_news[:3], indent=2, ensure_ascii=False))
    print(f"Total entries fetched in the past 2 hours: {len(zaobao_news)}")

if __name__ == "__main__":
    main()
