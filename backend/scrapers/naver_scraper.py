import asyncio
from playwright.async_api import async_playwright

class NaverShoppingScraper:
    async def get_trends(self):
        # Categories: Fashion(50000000), Digital(50000003), Food(50000006), Living(50000008)
        categories = {
            "50000000": "Fashion",
            "50000003": "Digital",
            "50000006": "Food",
            "50000008": "Living"
        }
        all_trends = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                    viewport={"width": 1920, "height": 1080}
                )
                
                # Scrape first 2 categories to save time, or round-robin? 
                # Let's do all 4 but limit items per category to keep it fast
                for cid, cat_name in categories.items():
                    target_url = f"https://datalab.naver.com/shoppingInsight/sCategory.naver?cid={cid}"
                    print(f"Scraping Naver {cat_name} Category ({cid})...")
                    
                    try:
                        page = await context.new_page()
                        await page.goto(target_url, wait_until="domcontentloaded", timeout=20000)
                        
                        # FORCE CLICK 'Inquiry' button to ensure data loads for this CID
                        try:
                            # Wait for button then click
                            await asyncio.sleep(2) # Stabilize
                            await page.wait_for_selector(".btn_submit", timeout=5000)
                            await page.click(".btn_submit")
                            await asyncio.sleep(2) # Wait for AJAX reload
                        except Exception as e:
                            print(f"Warning: Could not click submit button: {e}")

                        # Wait for list (fast timeout since we expect it)
                        try:
                            # increased timeout to 10s
                            await page.wait_for_selector(".rank_top1000_list li a", timeout=10000)
                        except:
                            # Fallback: click simple submit if needed, or just skip
                            print(f"Timeout waiting for {cat_name} list.")
                            pass
                        
                        items = await page.query_selector_all(".rank_top1000_list li a")
                        print(f"Found {len(items)} items for {cat_name}")
                        
                        count = 0
                        for item in items: 
                            if count >= 10:  # Top 10 per category
                                break
                            
                            full_text = await item.inner_text()
                            parts = full_text.split('\n')
                            keyword = parts[1].strip() if len(parts) > 1 else full_text.strip()
                            all_trends.append(keyword)
                            count += 1
                            
                        await page.close()
                        await asyncio.sleep(1) # Polite delay
                        
                    except Exception as e:
                        print(f"Error scraping Naver {cat_name}: {e}")
                
                await browser.close()
                
        except Exception as e:
            print(f"Playwright error: {e}")
            
        # Shuffle or just return logic? 
        return all_trends

if __name__ == "__main__":
    scraper = NaverShoppingScraper()
    print(asyncio.run(scraper.get_trends()))
