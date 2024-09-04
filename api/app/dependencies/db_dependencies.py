import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from app.settings import DatabaseSettings

# Dependency to initialize the database client
def get_db():
    mongo_db = None
    if os.environ.get("PRODUCTION") == "True":
        uri = f"mongodb+srv://{DatabaseSettings.MONGO_USERNAME.value}:{DatabaseSettings.MONGO_PASSWORD.value}@{DatabaseSettings.MONGO_CLUSTER.value}/?retryWrites=true&w=majority&appName=ClusterSportReg"
        mongo_db = MongoClient(uri)
        # Send a ping to confirm a successful connection
        try:
            mongo_db.admin.command('ping')
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

    else:
        mongo_db = MongoClient("mongodb://bd-sportreg-dev:27017/",
                                   username=DatabaseSettings.MONGO_USERNAME.value,
                                   password=DatabaseSettings.MONGO_PASSWORD.value)

    # Get the database
    mongo_db = mongo_db["sportreg"]

    return mongo_db
