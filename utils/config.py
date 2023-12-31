from peewee import SqliteDatabase
import json

# Get config from json file
jsonFile = open("config.json", "r")
configData = json.loads(jsonFile.read())


# Setup constants
INACTIVE_DAYS = int(configData["inactive_days"])
DATABASE_PATH = configData["database_path"]


# Setup Database
database = SqliteDatabase(configData["database_path"],pragmas={'foreign_keys': 1})
