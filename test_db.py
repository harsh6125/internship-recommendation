# test_db.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

MONGO_URI = "mongodb://localhost:27017/"

try:
    # We add a serverSelectionTimeoutMS to make it fail faster if it can't connect
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("✅ Success! Your Python script can connect to your local MongoDB.")
except ConnectionFailure as e:
    print(f"❌ Connection Failed: Could not connect to MongoDB.")
    print(f"   Details: {e}")
    print("\n   Troubleshooting:")
    print("   1. Is the 'MongoDB Server' service running in services.msc?")
    print("   2. Is a firewall blocking the connection on port 27017?")