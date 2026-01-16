import os
import json
import urllib.request
from datetime import datetime, timedelta

class NaverDataLab:
    def __init__(self):
        # Prefer env vars, fallback to provided keys (safe for this local app)
        self.client_id = os.getenv("NAVER_CLIENT_ID", "XcqIIExatxy29XoZ6RHC")
        self.client_secret = os.getenv("NAVER_CLIENT_SECRET", "I1jOucavL2")
        self.url = "https://openapi.naver.com/v1/datalab/search"

    def get_daily_trend(self, keyword: str, days: int = 30):
        """
        Fetch daily trend ratio for the specified number of days (default: 30).
        Returns:
            list: [{"date": "2024-01-01", "ratio": 12.5}, ...]
        """
        try:
            # Set date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            body = {
                "startDate": start_date.strftime("%Y-%m-%d"),
                "endDate": end_date.strftime("%Y-%m-%d"),
                "timeUnit": "date" if days <= 30 else "week" if days > 365 else "date", # Use 'week' for very long ranges if needed, but 'date' is fine for 1 year
                "keywordGroups": [
                    {"groupName": keyword, "keywords": [keyword]}
                ],
                # "device": "pc", # Optional: 'pc' or 'mo'
                # "gender": "f",  # Optional
                # "ages": ["1", "2"] # Optional
            }
            
            request = urllib.request.Request(self.url)
            request.add_header("X-Naver-Client-Id", self.client_id)
            request.add_header("X-Naver-Client-Secret", self.client_secret)
            request.add_header("Content-Type", "application/json")
            
            response = urllib.request.urlopen(request, data=json.dumps(body).encode("utf-8"))
            res_code = response.getcode()
            
            if res_code == 200:
                response_body = response.read().decode('utf-8')
                data = json.loads(response_body)
                
                # Extract results
                # Response structure: { "results": [ { "title": "...", "keywords": [...], "data": [ { "period": "2024-01-01", "ratio": 15.3 }, ... ] } ] }
                if data.get('results'):
                    trend_data = data['results'][0]['data']
                    # Normalize keys just in case, though API returns 'period' and 'ratio'
                    return [{"date": item["period"], "ratio": item["ratio"]} for item in trend_data]
                
            return []
            
        except Exception as e:
            print(f"[NaverDataLab] Error fetching trend for {keyword}: {e}")
            return []
