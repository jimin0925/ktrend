from backend.scrapers.naver_scraper import NaverShoppingScraper
import time

def test():
    print("Starting Sync Scraper Test (Single Category)...")
    start_time = time.time()
    scraper = NaverShoppingScraper()
    trends = scraper.get_trends()
    print(f"Scraping completed in {time.time() - start_time:.2f} seconds")
    print(f"Found {len(trends)} trends:")
    print(trends)

if __name__ == "__main__":
    test()
