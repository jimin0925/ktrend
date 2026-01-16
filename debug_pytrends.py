from pytrends.request import TrendReq

def test_pytrends():
    print("Testing pytrends...")
    try:
        pytrends = TrendReq(hl='ko', tz=540)
        # Get Realtime Search Trends
        # trending_searches = pytrends.trending_searches(pn='south_korea') # pn name might differ
        
        # trending_searches usually returns a DataFrame
        # print(trending_searches.head())
        
        # Try daily trends
        daily_trends = pytrends.trending_searches(pn='south_korea')
        print("Success fetching daily trends!")
        print(daily_trends.head())
        
    except Exception as e:
        print(f"Error with pytrends: {e}")

if __name__ == "__main__":
    test_pytrends()
