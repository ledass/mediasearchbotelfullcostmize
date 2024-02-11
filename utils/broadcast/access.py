import info
from utils.broadcast.db import Database
from info import DATABASE_URI, BROADCAST_DB_NAME

db = Database(info.DATABASE_URI, BROADCAST_DB_NAME)
