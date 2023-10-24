#Database updater
#Delete gymbros.db, then run this to update database
import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

#Start database from scratch
def initialise_db():
    #Make table containing all users' data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            username TEXT PRIMARY KEY,
            password TEXT,
            coords TEXT,
            membership TEXT,
            style TEXT,
            deadlift INTEGER,
            squat INTEGER,
            bench INTEGER,
            overhead INTEGER,
            schedule TEXT
        )
    """)

    connection.commit()

initialise_db()

#Insert existing/seed data (because there are so many criteria I'm not gonna do it manually every time lol)
seeddata = [
("ronniepickering", "doyouknowwhoiam", "52.203877248629254, 20.965159296723883", "artis", "bodybuilding", 125, 125, 125, 125, "monday,tuesday,wednesday"),
("mudwizard", "dropoutoflife", "52.23122168568795, 20.95108306546127", "zdrofit", "powerlifting", 300, 200, 175, 125, "monday,tuesday,wednesday,thursday"),
("ozzyosbourne", "allaboard","52.24737393593506, 21.014812388173574", "totalfitness", "bodybuilding", 150, 140, 100, 80, "monday,wednesday,friday"),
("mikolajszywala", "aceed", "52.15182950616367, 21.06355143963846", "artis", "bodybuilding", 5, 5, 180, 100, "monday,tuesday,wednesday,thursday,friday,saturday"),
("auba", "meyang","52.224173181636694, 21.007969059592277", "artis", "bodybuilding", 100, 100, 100, 100, "monday,wednesday,friday,sunday")
]
for item in seeddata:
    cursor.execute("""
        INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, item)
connection.commit()
connection.close()