import asyncio
from playwright.async_api import async_playwright

class YoutubeScraper:
    async def get_trends(self):
        url = "https://www.youtube.com/feed/trending"
        trends = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=["--disable-blink-features=AutomationControlled"]
                )
                
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
                    locale="ko-KR", 
                    timezone_id="Asia/Seoul"
                )
                
                page = await context.new_page()
                print(f"Navigating to {url}...")
                
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(3) # Wait for network
                    
                    # Wait for video titles
                    try:
                        await page.wait_for_selector("#video-title", timeout=15000)
                    except:
                        pass
                        
                    titles = await page.query_selector_all("#video-title")
                    
                    count = 0
                    for title in titles:
                        if count >= 10:
                            break
                        
                        text = await title.inner_text()
                        if text:
                            trends.append(text.strip())
                            count += 1
                            
                except Exception as e:
                    print(f"Error scraping YouTube: {e}")
                
                await browser.close()
                
        except Exception as e:
            print(f"Playwright error: {e}")
            
        return trends
