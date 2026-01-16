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
        
    async def get_trends(self, source: str = "all"):
        """
        Fetch trends from specified source using Playwright scrapers (Async).
        
        Includes simple in-memory caching (1 hour) to prevent blocking/slowness.
        """
        # Check cache
        print("\n\n [!!!] COLLECTOR IS RUNNING NEW CODE [!!!] \n\n")
        cache_key = source
        if cache_key in self._cache and datetime.now() < self._cache_expiry.get(cache_key, datetime.min):
            print(f"[CACHE HIT] Returning cached trends for {source}")
            return self._cache[cache_key]

        print(f"[CACHE MISS] Fetching fresh trends for {source}...")
        trends = []
        try:
            import asyncio
            
            if source in ["shopping", "all"]:
                from backend.scrapers.naver_scraper import NaverShoppingScraper
                print(" -> Invoking NaverShoppingScraper (Async)...")
                # Naver scraper is now ASYNC
                naver_trends = await NaverShoppingScraper().get_trends()
                print(f" -> NaverShoppingScraper returned {len(naver_trends)} items")
                trends.extend([{"keyword": t, "source": "Naver Shopping"} for t in naver_trends])
                
            if source in ["youtube", "all"]:
                try:
                    from backend.scrapers.youtube_scraper import YoutubeScraper
                    print(" -> Invoking YoutubeScraper (Async)...")
                    youtube_trends = await YoutubeScraper().get_trends()
                    print(f" -> YoutubeScraper returned {len(youtube_trends)} items")
                    trends.extend([{"keyword": t, "source": "YouTube"} for t in youtube_trends])
                except Exception as e:
                    print(f" -> [WARNING] YouTube scraper failed: {e}")
                    # Continue with whatever trends we have (e.g. Naver)
                
            # If all failed, return mock
            if not trends:
                print(" -> [WARNING] No trends found. Returning MOCK data (NOT CACHING).")
                return self.get_mock_trends()
            
            # Update cache ONLY if valid trends
            print(f" -> [CACHE SET] Storing {len(trends)} items in cache for {source}")
            self._cache[cache_key] = trends
            self._cache_expiry[cache_key] = datetime.now() + timedelta(hours=1)
            
            return trends
            
        except Exception as e:
            print(f" -> [ERROR] Error in get_trends: {e}")
            return self.get_mock_trends()

    def get_mock_trends(self):
        return [{"keyword": t, "source": "Mock"} for t in [
            "두바이 초콜릿",
            "피스타치오",
            "선재 업고 튀어",
            "뉴진스",
            "한강 작가",
            "아이폰 16",
            "삼성전자",
            "기아 타이거즈",
            "흑백요리사",
            "티니핑"
        ]]

    def get_google_daily_trends(self, geo="KR"):
        # Deprecated in favor of get_trends
        return [t["keyword"] for t in self.get_trends(source="all")]
