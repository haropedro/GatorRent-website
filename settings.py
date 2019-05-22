import os
from os.path import join, dirname, abspath 
from dotenv import load_dotenv

dotenv_path = abspath(join(dirname(__file__), '..' ,'.env'))
load_dotenv(dotenv_path)

# database configuration
database = {
    'user': 'root',
    'password': os.getenv('DB_PSSWRD'),
    'host': 'db',
    'port': '3306',
    'database': 'gatorrent_db'
}