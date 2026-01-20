from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn
import asyncio
from contextlib import asynccontextmanager

from backend.services.collector import TrendCollector
from backend.services.analyzer import TrendAnalyzer
from backend.services.naver_datalab import NaverDataLab
import os

# Initialize Services
collector = TrendCollector()
analyzer = TrendAnalyzer()
datalab_service = NaverDataLab()

# Background Scheduler
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("[SYSTEM] Starting Background Scheduler...")
    scheduler.add_job(collector.collect_all_and_save, 'interval', hours=1)
    scheduler.start()
    
    # Run initial collection in background (fire and forget)
    asyncio.create_task(collector.collect_all_and_save())
    
    yield
    
    # Shutdown
    print("[SYSTEM] Shutting down Scheduler...")
    scheduler.shutdown()

app = FastAPI(title="Korea Trend API", description="API for Korea Trend Website", version="1.0.0", lifespan=lifespan)

# CORS Config
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://ktrend.vercel.app",
    "https://trand-web-project.vercel.app",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Korea Trend API is running"}

@app.get("/api/manual-update")
async def manual_update():
    """
    Manually trigger trend collection (bypasses scheduler).
    Useful if server slept and missed a scheduled job.
    """
    print("[MANUAL] Triggering manual update...")
    await collector.collect_all_and_save()
    return {"status": "success", "message": "Trends updated manually"}

@app.get("/api/trends")
async def read_trends(category: str = "all"):
    """
    Get top trends.
    Returns cached data if available.
    Reason is now fetched on-demand via /api/analyze to save costs/time.
    """
    first_source = "shopping" if category != "all" else "all" # optimize source? No, collector handles it.
    trends_data = await collector.get_trends(source="all", category_filter=category)
    
    # Transform to object
    results = []
    
    for idx, item in enumerate(trends_data):
        keyword = item["keyword"] if isinstance(item, dict) else item
        source = item.get("source", "Unknown") if isinstance(item, dict) else "Google/Mock"
        
        results.append({
            "rank": idx + 1,
            "keyword": keyword,
            "reason": "AI 분석을 위해 클릭하세요", # Placeholder
            "source": source,
            "category": category
        })
        
    # Extract timestamp from the first item (assuming sorted batch)
    last_updated = None
    if trends_data and isinstance(trends_data[0], dict):
        last_updated = trends_data[0].get("created_at")

    return {
        "category": category,
        "last_updated": last_updated,
        "trends": results
    }

@app.get("/api/analyze/{keyword}")
async def analyze_trend_api(keyword: str):
    """
    Analyze why a keyword is trending using LLM + Search + Naver Data.
    """
    result = await analyzer.analyze_trend(keyword)
    return result

@app.get("/api/trend-data/{keyword}")
async def get_trend_data(keyword: str, period: str = "1mo"):
    """
    Fetch only the trend chart data for a specific period.
    period: "1mo" (30 days) or "1yr" (365 days).
    """
    from backend.services.naver_datalab import NaverDataLab
    import asyncio
    
    days = 365 if period == "1yr" else 30
    
    try:
        datalab_service = NaverDataLab()
        chart_data = await asyncio.to_thread(datalab_service.get_daily_trend, keyword, days)
        return {"keyword": keyword, "period": period, "chart_data": chart_data}
    except Exception as e:
        print(f"Error fetching trend data: {e}")
        return {"keyword": keyword, "period": period, "chart_data": []}
