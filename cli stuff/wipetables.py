import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

#cursor.execute("DROP TABLE IF EXISTS friends")
#cursor.execute("DROP TABLE IF EXISTS users")
connection.commit()
connection.close()