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
            schedule TEXT,
            monthsvolume INTEGER
        )
    """)

    connection.commit()

initialise_db()

#Insert existing/seed data (because there are so many criteria I'm not gonna do it manually every time lol)
seeddata = [
("ronniepickering", "doyouknowwhoiam", "52.203877248629254, 20.965159296723883", "artis", "bodybuilding", 125, 125, 125, 125, "Monday,Tuesday,Wednesday", 31250),
("mudwizard", "dropoutoflife", "52.23122168568795, 20.95108306546127", "zdrofit", "powerlifting", 300, 200, 175, 125, "Monday,Tuesday,Wednesday,Thursday", 60000),
("ozzyosbourne", "allaboard","52.24737393593506, 21.014812388173574", "totalfitness", "bodybuilding", 150, 140, 100, 80, "Monday,Wednesday,Friday", 36725),
("mikolajszywala", "gymbeast123", "52.217912083076904 21.078752667694", "artis", "bodybuilding", 190, 160, 125, 70, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday", 49050),
("auba", "meyang","52.224173181636694, 21.007969059592277", "artis", "bodybuilding", 100, 100, 100, 100, "Monday,Wednesday,Friday,Sunday", 28000),
("ron", "burgundy", "52.279475849766214 21.116083325254532", "cityfit", "crossfit", 25, 128, 21, 57, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", 16170),
('donaldduck', 'ihatescroogemcduck', '52.165762713714436 21.08251053108417', 'calypso', 'olympic', 300, 250, 20, 15, 'Friday,Saturday,Sunday', 55575)
]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule, monthsvolume)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
    except:
        pass
connection.commit()
connection.close()