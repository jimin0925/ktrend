import asyncio
from backend.scrapers.naver_scraper import NaverShoppingScraper
from backend.scrapers.youtube_scraper import YoutubeScraper
import time

async def test():
    print("--- Testing Naver scraper ---")
    start = time.time()
    try:
        naver = NaverShoppingScraper()
        trends = await naver.get_trends()
        print(f"Naver Result ({time.time()-start:.2f}s):", trends)
    except Exception as e:
        print(f"Naver Failed: {e}")

    print("\n--- Testing YouTube scraper ---")
    start = time.time()
    try:
        yt = YoutubeScraper()
        trends = await yt.get_trends()
        print(f"YouTube Result ({time.time()-start:.2f}s):", trends)
    except Exception as e:
        print(f"YouTube Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test())
