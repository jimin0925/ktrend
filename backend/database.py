import os
from supabase import create_client, Client
from datetime import datetime, timedelta

# Supabase Credentials (loaded from Env or hardcoded for now as requested)
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://vxafzadreiuifilbybxb.supabase.co")
# User provided 'sb_publishable_...' which seems to be the public anon key.
# If writes fail, we will need service_role key.
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "sb_publishable_zCqe4ibxMCR8YbL545gjHw_8v3H28FK")

class Database:
    def __init__(self):
        try:
            self.client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
            print(f"[DB] Connected to Supabase at {SUPABASE_URL}")
        except Exception as e:
            print(f"[DB] Connection failed: {e}")
            self.client = None

    def save_trends(self, category: str, trends: list):
        """
        Save a batch of trends to 'trends' table.
        replaces existing trends for this category?
        Strategy: Insert with current timestamp. We can query 'latest' by timestamp.
        """
        if not self.client: return
        
        try:
            # Prepare data
            rows = []
            now = datetime.now().isoformat()
            for rank, item in enumerate(trends):
                keyword = item["keyword"] if isinstance(item, dict) else item
                rows.append({
                    "category": category,
                    "keyword": keyword,
                    "rank": rank + 1,
                    "created_at": now
                })
                
            # Insert
            # Note: If RLS is enabled and Anon key doesn't have INSERT permission, this will fail.
            print(f"[DB] Saving {len(rows)} trends for {category}...")
            # We assume table 'trends' exists.
            self.client.table("trends").insert(rows).execute()
            print("[DB] Trends saved successfully.")
        except Exception as e:
            print(f"[DB] Failed to save trends: {e}")

    def get_latest_trends(self, category: str):
        """
        Get the most recent batch of trends for a category.
        """
        if not self.client: return []
        
        try:
            # Subquery strategy is complex in simple API.
            # Simple strategy: Fetch last 20 items for category order by created_at desc
            # This might mix multiple batches if we are not careful.
            # Better: Fetch latest created_at for this category first?
            # Or just fetch last 100 and dedup in python.
            # Let's try to order by created_at desc limit 20.
            
            response = self.client.table("trends") \
                .select("*") \
                .eq("category", category) \
                .order("created_at", desc=True) \
                .limit(20) \
                .execute()
            
            data = response.data
            
            # Post-process: Filter to include only the very latest batch?
            # If we fetch 20, and batch size is 10, we might get 2 batches.
            # We should group by 'created_at' batch.
            if not data: return []
            
            # Find the latest timestamp
            latest_ts = data[0]["created_at"]
            # Filter only items with that timestamp (allowing small window?)
            # Actually, created_at might differ slightly if inserted mostly same time.
            # Ideally we insert with same timestamp string.
            
            # Grouping by timestamp
            latest_batch = [item for item in data if item["created_at"] == latest_ts]
            
            # If batch is small (e.g. 1 item?), maybe fallback?
            # Assuming batch insert uses identical string timestamp.
            
            # Sort by rank
            latest_batch.sort(key=lambda x: x["rank"])
            
            # Format back to simple list/dict
            formatted = [{"keyword": item["keyword"], "rank": item["rank"], "category": item["category"], "created_at": item["created_at"]} for item in latest_batch]
            print(f"[DB] Loaded {len(formatted)} trends from DB for {category}")
            return formatted
            
        except Exception as e:
            print(f"[DB] Failed to get latest trends: {e}")
            return []

    def save_analysis(self, keyword: str, reason: str, chart_data: list):
        """
        Save/Upsert analysis result.
        """
        if not self.client: return
        
        try:
            now = datetime.now().isoformat()
            data = {
                "keyword": keyword,
                "reason": reason,
                "chart_data": chart_data,
                "updated_at": now
            }
            
            # Upsert (requires primary key on keyword)
            self.client.table("trend_analysis").upsert(data).execute()
            print(f"[DB] Saved analysis for '{keyword}'")
        except Exception as e:
            print(f"[DB] Failed to save analysis: {e}")

    def get_analysis(self, keyword: str):
        """
        Get analysis for a keyword.
        """
        if not self.client: return None
        
        try:
            response = self.client.table("trend_analysis") \
                .select("*") \
                .eq("keyword", keyword) \
                .execute()
                
            if response.data:
                item = response.data[0]
                # Optional: Check staleness (e.g. valid for 24h)
                # For now, return permanent history
                return {
                    "keyword": item["keyword"],
                    "reason": item["reason"],
                    "chart_data": item["chart_data"]
                }
            return None
        except Exception as e:
            print(f"[DB] Failed to get analysis: {e}")
            return None
