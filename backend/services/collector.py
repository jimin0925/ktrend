import os
import urllib.request
import json
from datetime import datetime, timedelta

# Naver API credentials should be loaded from env or passed in
# For now, we will structure the class to accept them

class TrendCollector:
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self._cache = {}
        self._cache_expiry = {}
        
    async def get_trends(self, source: str = "all", category_filter: str = "all"):
        """
        Fetch trends from specified source using Playwright scrapers (Async).
        
        Includes simple in-memory caching (1 hour) to prevent blocking/slowness.
        """
        # Check cache
        cache_key = f"{source}_{category_filter}"
        if cache_key in self._cache and datetime.now() < self._cache_expiry.get(cache_key, datetime.min):
            print(f"[CACHE HIT] Returning cached trends for {cache_key}")
            return self._cache[cache_key]

        print(f"[CACHE MISS] Fetching fresh trends for {source}...")
        trends = []
        try:
            import asyncio
            
            if source in ["shopping", "all"]:
                from backend.scrapers.naver_scraper import NaverShoppingScraper
                print(" -> Invoking NaverShoppingScraper (Async)...")
                # Naver scraper returns [{"keyword": "...", "category": "..."}, ...]
                naver_trends_raw = await NaverShoppingScraper().get_trends()
                
                for item in naver_trends_raw:
                    # Item is dict now
                    kw = item["keyword"]
                    cat = item["category"]
                    
                    # Filter logic
                    if category_filter != "all" and cat != category_filter:
                        continue
                        
                    trends.append({"keyword": kw, "source": "Naver Shopping", "category": cat})
                
            if source in ["youtube", "all"] and category_filter == "all":
                 # YouTube scraping logic (unchanged, mainly for 'all' or 'youtube' source)
                try:
                    from backend.scrapers.youtube_scraper import YoutubeScraper
                    print(" -> Invoking YoutubeScraper (Async)...")
                    youtube_trends = await YoutubeScraper().get_trends()
                    trends.extend([{"keyword": t, "source": "YouTube", "category": "General"} for t in youtube_trends])
                except Exception as e:
                    print(f" -> [WARNING] YouTube scraper failed: {e}")
                
            # If all failed, return mock
            if not trends:
                print(" -> [WARNING] No trends found. Returning MOCK data (NOT CACHING).")
                return self.get_mock_trends(category_filter)
            
            # Update cache
            print(f" -> [CACHE SET] Storing {len(trends)} items in cache for {cache_key}")
            self._cache[cache_key] = trends
            self._cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
            
            return trends
            
        except Exception as e:
            print(f" -> [ERROR] Error in get_trends: {e}")
            return self.get_mock_trends()

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
