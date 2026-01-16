import requests
from bs4 import BeautifulSoup

def get_naver_shopping_best():
    url = "https://search.shopping.naver.com/best/category/click?categoryCategoryId=ALL&viewType=list&sort=favorite&period=P1D"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Select product titles (Classes might change, so we look for common structures)
            # Generally, listed items have a specific class. 
            # Let's print the first few lines of text or try to find list items.
            
            # As of 2024, classes are obfuscated/dynamic (e.g. image_cell_wrapper__...).
            # But usually 'image_cell_wrapper' or 'product_info_main' exists?
            # Let's try to find 'div' with class matching 'product_title' or similar?
            # Or simplified: find all 'a' tags with some length and 'title' attribute?
            
            # Let's blindly try to extract text from a likely container.
            # Usually strict scraping requires inspection. 
            # For this debug, I will dump some text to see if we got the page content.
            
            print("Page Title:", soup.title.string)
            print("Text snippet:", soup.get_text()[:500])
            
            # Try to find specific product names if possible
            # We can look for <div class="imageProduct_title__..."> (example)
            # Actually, Naver Shopping is rendered with Next.js (SSR), so HTML should contain data.
            # Look for JSON in <script id="__NEXT_DATA__">.
            
            script = soup.find("script", {"id": "__NEXT_DATA__"})
            if script:
                print("Found NEXT_DATA script! We can parse JSON.")
                return True
            else:
                print("No NEXT_DATA found.")
                return False
                
        else:
            print(f"Failed to fetch Naver Shopping. Status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_naver_shopping_best()
