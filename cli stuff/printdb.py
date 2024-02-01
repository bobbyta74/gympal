#Print whole users table to make sure everything's fine and dandy
import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

workoutid = 4
result = cursor.execute("""
        SELECT * FROM workouts
    """).fetchall()

print(result)