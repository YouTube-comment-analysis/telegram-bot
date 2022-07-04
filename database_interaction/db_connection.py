import psycopg2 as db
from config import database_config

connection = db.connect(
    database=database_config['database'],
    user=database_config['user'],
    password=database_config['password'],
    host=database_config['host'],
    port=database_config['port']
)
