import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.services.collector import TrendCollector
from backend.services.analyzer import TrendAnalyzer

# Credentials from naver_data.py
CLIENT_ID = "XcqIIExatxy29XoZ6RHC"
CLIENT_SECRET = "I1jOucavL2"

def test_workflow():
    print("1. Collecting Trends (Google RSS)...")
    collector = TrendCollector(CLIENT_ID, CLIENT_SECRET)
    trends = collector.get_google_daily_trends()
    
    if not trends:
        print("Failed to get Google Trends.")
        return

    print(f"Found {len(trends)} trends. Top 3: {trends[:3]}")
    
    print("\n2. Analyzing Reason (Naver Search API)...")
    analyzer = TrendAnalyzer(CLIENT_ID, CLIENT_SECRET)
    
    # Test with the first real trend found
    target_keyword = trends[0]
    print(f"Analyzing '{target_keyword}'...")
    reason = analyzer.analyze_reason(target_keyword)
    print(f"Reason: {reason}")
    
    # Test with the example "피스타치오"
    print(f"\nAnalyzing '피스타치오' (Manual Check)...")
    reason_pistachio = analyzer.analyze_reason("피스타치오")
    print(f"Reason: {reason_pistachio}")

if __name__ == "__main__":
    test_workflow()
