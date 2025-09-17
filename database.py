# database.py

from pymongo import MongoClient

# Connection string for a local MongoDB instance
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "internshipDB"

try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    internship_collection = db["internships"]
    student_collection = db["students"]
    user_collection = db["users"]

    
    # Test the connection
    client.admin.command('ping')
    print("✅ Successfully connected to local MongoDB!")

except Exception as e:
    print(f"Error connecting to MongoDB: {e}")