#Print whole users table to make sure everything's fine and dandy
import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

criterion = "deadlift"
result = cursor.execute(f"""
        SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, monthsvolume, monthstimespent
        FROM users
        ORDER BY {criterion}
    """).fetchall()

print(result)