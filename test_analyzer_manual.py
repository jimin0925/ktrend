import asyncio
import os
from dotenv import load_dotenv
from backend.services.analyzer import TrendAnalyzer

# Load env for API Key
load_dotenv()

async def test_analysis():
    analyzer = TrendAnalyzer()
    
    if not analyzer.client:
        print("Skipping test: No OpenAI API Key found.")
        return

    # Test Case 1: Hallucination Risk (Name confusion)
    keyword1 = "두바이 쫀득쿠키"
    print(f"\n[Test 1] Analyzing '{keyword1}' (Viral)...")
    result1 = await analyzer.analyze_trend(keyword1)
    print(f" > Reason: {result1.get('reason')}")

    # Test Case 2: Seasonal Item
    keyword2 = "여성패딩"
    print(f"\n[Test 2] Analyzing '{keyword2}' (Seasonal)...")
    result2 = await analyzer.analyze_trend(keyword2)
    print(f" > Reason: {result2.get('reason')}")

    # Test Case 3: Steady Seller
    keyword3 = "물티슈"
    print(f"\n[Test 3] Analyzing '{keyword3}' (Steady)...")
    result3 = await analyzer.analyze_trend(keyword3)
    print(f" > Reason: {result3.get('reason')}")

    # Test Case 4: Ingredient of Viral Trend
    keyword4 = "피스타치오스프레드"
    print(f"\n[Test 4] Analyzing '{keyword4}' (Ingredient)...")
    result4 = await analyzer.analyze_trend(keyword4)
    print(f" > Reason: {result4.get('reason')}")
    chart_data = result4.get('chart_data', [])
    print(f" > Chart Data Points: {len(chart_data)}")
    if chart_data:
        print(f" > Sample Data: {chart_data[0]} ... {chart_data[-1]}")

if __name__ == "__main__":
    asyncio.run(test_analysis())
