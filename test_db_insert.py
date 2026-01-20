from backend.database import Database
import datetime

def test_insert():
    db = Database()
    print("Testing DB Connection and Insert...")
    
    dummy_trends = [
        {"keyword": "DB_WRITE_TEST_KEYWORD", "rank": 999, "category": "Test"}
    ]
    
    try:
        db.save_trends("Test", dummy_trends)
        print("Test Insert Finished (Check if successful above)")
    except Exception as e:
        print(f"Test Insert Failed: {e}")

if __name__ == "__main__":
    test_insert()
