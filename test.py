import requests
res=requests.get('https://zhibo.sina.com.cn/api/zhibo/feed?page=5&page_size=200&zhibo_id=152').json()
items=res['result']['data']['feed']['list']
print(f'Total items: {len(items)}')
print(f'Earliest item time: {items[-1].get("create_time")}')
print("Titles:")
for i in range(5):
    print(items[i].get('rich_text') or items[i].get('content'))
