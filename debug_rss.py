import requests

urls = [
    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=KR",
    "https://trends.google.co.kr/trends/trendingsearches/daily/rss?geo=KR",
    "https://trends.google.com/trends/hottrends/atom/feed?pn=p23",
    "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US" # Test US
]

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for url in urls:
    print(f"Testing {url}...")
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Content length: {len(response.content)}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
