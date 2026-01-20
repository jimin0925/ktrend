from datetime import datetime
from backend.database import Database

# Naver API credentials should be loaded from env or passed in
# For now, we will structure the class to accept them

class TrendCollector:
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.db = Database()

    async def get_trends(self, source: str = "all", category_filter: str = "all"):
        """
        Fetch trends:
        1. Try DB (FAST)
        2. If DB empty, Return Mock (FAST) + Trigger Background Scrape
        """
        # 1. Try DB
        print(f"[COLLECTOR] Fetching trends for {category_filter} from DB...")
        db_trends = self.db.get_latest_trends(category_filter)
        if db_trends:
            # Check Staleness Logic
            try:
                latest_ts_str = db_trends[0].get("created_at")
                if latest_ts_str:
                    from datetime import datetime, timedelta, timezone
                    # Supabase returns UTC ISO string usually with +00:00 or Z
                    # Safe parsing
                    latest_ts = datetime.fromisoformat(latest_ts_str.replace('Z', '+00:00'))
                    now = datetime.now(timezone.utc)
                    
                    if (now - latest_ts) > timedelta(hours=1):
                        print(f"[COLLECTOR] Data is STALE (Last update: {latest_ts_str}). Triggering background refresh.")
                        import asyncio
                        asyncio.create_task(self.collect_all_and_save())
                    else:
                        print(f"[COLLECTOR] Data is FRESH (Last update: {latest_ts_str}).")
            except Exception as e:
                print(f"[COLLECTOR] Error checking staleness: {e}. Ignoring.")

            print(f"[COLLECTOR] Found {len(db_trends)} items in DB.")
            return db_trends

        # 2. Failover: DB empty (Cold Start)
        # Instead of blocking for 60s to scrape, return Mocks immediately
        # and start scraping in the background.
        print(f"[COLLECTOR] DB empty. Returning MOCKS immediately and triggering background scrape.")
        
        import asyncio
        # Trigger full refresh in background
        asyncio.create_task(self.collect_all_and_save())
        
        # Return mock data instant response
        return self.get_mock_trends(category_filter)
        
    async def collect_all_and_save(self):
        """
        Background Job: Scrape ALL categories and save to DB.
        """
        print("[BACKGROUND] Starting hourly trend collection...")
        categories = ["Fashion", "Digital", "Food", "Living"]
        
        # 1. Scrape specific categories
        for cat in categories:
            print(f"[BACKGROUND] Scraping {cat}...")
            trends = await self._scrape_live("shopping", cat)
            if trends:
                self.db.save_trends(cat, trends)
                
        # 2. Scrape "all" (Integrated)
        print(f"[BACKGROUND] Scraping Integrated...")
        trends_all = await self._scrape_live("all", "all")
        if trends_all:
            self.db.save_trends("all", trends_all)
            
        print("[BACKGROUND] Collection complete.")

    async def _scrape_live(self, source, category_filter):
        """
        Internal method to reuse scraping logic.
        """
        trends = []
        try:
            import asyncio
            
            if source in ["shopping", "all"] or category_filter != "all":
                from backend.scrapers.naver_scraper import NaverShoppingScraper
                # Naver scraper returns [{"keyword": "...", "category": "..."}, ...]
                # Optimization: Pass category to scraper if supported?
                # Currently scraper fetches ALL. Ideally we optimize scraper to fetch only target.
                # But current scraper fetches all 4. 
                # Let's just filter.
                print(" -> Invoking NaverShoppingScraper (Async)...")
                naver_trends_raw = await NaverShoppingScraper().get_trends()
                
                for item in naver_trends_raw:
                    kw = item["keyword"]
                    cat = item["category"]
                    
                    if category_filter != "all" and cat != category_filter:
                        continue
                    
                    trends.append({"keyword": kw, "source": "Naver Shopping", "category": cat})
            
            # YouTube (only for 'all' or specific youtube tab?)
            # Assuming YouTube is general
            if source in ["youtube", "all"] and category_filter == "all":
                try:
                    from backend.scrapers.youtube_scraper import YoutubeScraper
                    print(" -> Invoking YoutubeScraper (Async)...")
                    youtube_trends = await YoutubeScraper().get_trends()
                    trends.extend([{"keyword": t, "source": "YouTube", "category": "General"} for t in youtube_trends])
                except Exception as e:
                    print(f" -> [WARNING] YouTube scraper failed: {e}")
                
            if not trends:
                print(" -> [WARNING] No trends found. Returning MOCK data.")
                return self.get_mock_trends(category_filter)
            
            return trends
            
        except Exception as e:
            print(f"[ERROR] Live scrape failed: {e}")
            return self.get_mock_trends(category_filter)

    def get_mock_trends(self, category_filter="all"):
        mocks = {
            "all": ["두바이 초콜릿", "피스타치오", "아이폰 16", "선재 업고 튀어", "흑백요리사", "티니핑", "삼성전자", "기아 타이거즈"],
            "Fashion": ["여성 패딩", "니트 조끼", "롱부츠", "숏패딩", "머플러", "바라클라바"],
            "Digital": ["아이폰 16", "갤럭시 S24", "맥북 프로", "소니 헤드폰", "닌텐도 스위치", "로지텍 마우스"],
            "Food": ["두바이 초콜릿", "피스타치오 스프레드", "샤인머스캣", "그릭요거트", "마라탕", "탕후루"],
            "Living": ["크리스마스 트리", "가습기", "온수매트", "극세사 이불", "암막 커튼", "다이어리"]
        }
        
        selected_mocks = mocks.get(category_filter, mocks["all"])
        
        return [{"keyword": t, "source": "Mock", "category": category_filter} for t in selected_mocks]

    def get_google_daily_trends(self, geo="KR"):
        # Deprecated in favor of get_trends
        return [t["keyword"] for t in self.get_trends(source="all")]
