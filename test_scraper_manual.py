from backend.scrapers.naver_scraper import NaverShoppingScraper
import time

print("Starting Manual Scraper Test...")
start_time = time.time()
try:
    scraper = NaverShoppingScraper()
    trends = scraper.get_trends()
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds")
    print(f"Found {len(trends)} trends:")
    print(trends)
except Exception as e:
    print(f"Scraper failed with error: {e}")
