import sqlite3

# Setting up the connection
DB_PATH = "./data/database.db"
connection = sqlite3.connect(DB_PATH)

# Cursor
cur = connection.cursor()

# Commit changes
def commit():
    connection.commit()

# Initialize database tables
def build():
    query = """
        CREATE TABLE IF NOT EXISTS Roster(
            id INTEGER,
            nick TEXT,
            guild_id INTEGER,
            PRIMARY KEY(id, guild_id)
        );"""
    cur.execute(query)
    commit()
    
    query = """
        CREATE TABLE IF NOT EXISTS Tournaments(
            guild_id INTEGER PRIMARY KEY,
            react_message_id INTEGER,
            tourny_started INTEGER
        );"""

    cur.execute(query)
    commit()

    query = """
        CREATE TABLE IF NOT EXISTS Matches(
            guild_id INTEGER,
            match_num INTEGER,
            round INTEGER,
            player_one TEXT,
            player_two TEXT,
            PRIMARY KEY(guild_id, match_num)
        );"""

    cur.execute(query)
    commit()

# Execute a command
def execute(command, *values):
    cur.execute(command, tuple(values))
    commit()

# Fetch values from database
def fetch(command, *values):
    cur.execute(command, tuple(values))
    return cur.fetchall()