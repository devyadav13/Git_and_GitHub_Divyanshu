"""
Local verification script (NOT part of the deliverable app):
Uses mongomock to simulate MongoDB Atlas so we can prove the success/redirect
logic works end-to-end without needing live Atlas credentials in this sandbox.
"""
import app as flaskapp
import mongomock

# Patch the collection with a mongomock in-memory collection
fake_client = mongomock.MongoClient()
flaskapp.collection = fake_client["flask_mongo_db"]["submissions"]
flaskapp.mongo_connect_error = None

client = flaskapp.app.test_client()

resp = client.post("/submit", data={
    "name": "Divyanshu Yadav",
    "email": "divyanshu@example.com",
    "message": "Hello MongoDB Atlas!"
}, follow_redirects=False)

print("STATUS:", resp.status_code)
print("LOCATION HEADER:", resp.headers.get("Location"))

resp2 = client.get("/success")
print("\n--- /success page body snippet ---")
body = resp2.get_data(as_text=True)
print(body[body.find("<body>"):body.find("</body>")+7])

print("\n--- Document actually stored in the (mock) MongoDB collection ---")
for doc in flaskapp.collection.find():
    print(doc)
