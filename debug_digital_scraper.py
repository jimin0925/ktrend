import asyncio
from playwright.async_api import async_playwright

async def debug_digital():
    target_url = "https://datalab.naver.com/shoppingInsight/sCategory.naver?cid=50000003"
    print(f"Debug: Navigating to {target_url} (Digital)...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True) # Set headless=False to see it if local, but I can't.
        page = await browser.new_page()
        
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            print("Debug: Page loaded.")
            
            # SNAPSHOT to see what's happening
            # await page.screenshot(path="debug_digital_initial.png") 
            
            # Check button
            btn = await page.query_selector(".btn_submit")
            if btn:
                print("Debug: Found submit button. Clicking...")
                await btn.click()
                await asyncio.sleep(3)
            else:
                print("Debug: Submit button NOT found.")

            # Check list
            try:
                await page.wait_for_selector(".rank_top1000_list li a", timeout=10000)
                print("Debug: List appears.")
            except:
                print("Debug: Timeout waiting for list.")
                content = await page.content()
                print(f"Debug: Page content length: {len(content)}")
                # print(content[:500]) # Preview
                return

            items = await page.query_selector_all(".rank_top1000_list li a")
            print(f"Debug: Found {len(items)} items.")
            
            for i, item in enumerate(items[:5]):
                txt = await item.inner_text()
                print(f" - {i+1}: {txt.strip()}")
                
        except Exception as e:
            print(f"Debug: Error detected: {e}")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_digital())
