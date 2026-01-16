import asyncio
from backend.services.collector import TrendCollector

async def populate():
    print("Starting manual DB population...")
    collector = TrendCollector()
    
    # Run the collection logic (scrapes all categories -> saves to DB)
    await collector.collect_all_and_save()
    
    print("Manual population complete!")

if __name__ == "__main__":
    asyncio.run(populate())
