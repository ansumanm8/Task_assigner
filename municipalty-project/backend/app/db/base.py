from pymongo import MongoClient
import urllib.parse
from app.core.config import DATABASE_LOGIN_USERNAME ,DATABASE_LOGIN_PASSWORD

username = username = urllib.parse.quote_plus(DATABASE_LOGIN_USERNAME)
password = urllib.parse.quote_plus(DATABASE_LOGIN_PASSWORD)
uri = f"mongodb+srv://{username}:{password}@dev-test.turat6y.mongodb.net/?retryWrites=true&w=majority"
# Create a new client and connect to the server
client = MongoClient(uri)
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

db = client['mta_project']
usersCol = db['users']
tasksCol = db['task']