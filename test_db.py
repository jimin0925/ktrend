from backend.database import Database
import time

def test_db():
    db = Database()
    
    # 1. Test Write
    print("Testing DB Write...")
    test_data = [{"keyword": "TEST_KEYWORD", "category": "Test"}]
    db.save_trends("Test", test_data)
    
    # 2. Test Read
    print("Testing DB Read...")
    time.sleep(1)
    trends = db.get_latest_trends("Test")
    
    if trends:
        print("SUCCESS: Read back data:", trends)
    else:
        print("FAILURE: Could not read back data. (Check RLS policies?)")

if __name__ == "__main__":
    test_db()
