#Print whole users table to make sure everything's fine and dandy
import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

result = cursor.execute("""
    SELECT * FROM users
""").fetchall()

print(result)