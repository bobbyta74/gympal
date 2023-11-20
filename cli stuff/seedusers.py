#Database updater
#Delete gymbros.db, then run this to update database
import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

#Make users table
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
        volume INTEGER,
        timespent INTEGER
    )
""")
connection.commit()
#Insert existing/seed data (because there are so many criteria I'm not gonna do it manually every time lol)
seeddata = [
("ronniepickering", "doyouknowwhoiam", "52.20387 20.96515", "artis", "bodybuilding", 125, 125, 125, 125, "Monday,Tuesday,Wednesday", 31250, 547),
("mudwizard", "dropoutoflife", "52.23122 20.95108", "zdrofit", "powerlifting", 300, 200, 175, 125, "Monday,Tuesday,Wednesday,Thursday", 60000, 912),
("ozzyosbourne", "allaboard","52.24737 21.01481", "totalfitness", "bodybuilding", 150, 140, 100, 80, "Monday,Wednesday,Friday", 36725, 408),
("mikolajszywala", "gymbeast123", "52.21791 21.07875", "artis", "bodybuilding", 190, 160, 125, 70, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday", 49050, 3360),
("auba", "meyang","52.22417 21.00796", "artis", "bodybuilding", 100, 100, 100, 100, "Monday,Wednesday,Friday,Sunday", 28000, 1072),
("ron", "burgundy", "52.27947 21.11608", "cityfit", "crossfit", 25, 128, 21, 57, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", 16170, 559),
('donaldduck', 'screwunclescrooge', '52.16576 21.08251', 'calypso', 'olympic', 300, 250, 20, 15, 'Friday,Saturday,Sunday', 55575, 746),
("mikelarteta", "thegaffer", "52.22035 21.04087", "artis", "bodybuilding", 200, 150, 130, 85, "Monday,Tuesday,Thursday", 0, 0), 
('kai', 'havertz', '52.23271 21.01853', 'artis', 'bodybuilding', 95, 86, 60, 40, 'Monday,Wednesday,Friday', 1597, 75), 
('cliffburton', 'anesthesia', '52.24963 21.23084', 'artis', 'bodybuilding', 180, 165, 135, 75, 'Wednesday,Saturday,Sunday', 0, 0),
('michalgladyszczak', 'legenddesgrime', '52.18808 20.98865', 'artis', 'bodybuilding', 130, 125, 90, 45, 'Tuesday,Thursday,Saturday', 1940, 35)
]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule, volume, timespent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, item)
    except:
        pass

#Make friends table
#user1 = initiator, user2 = requested, status = 0 or 1 depending on whether friend accepted or not
cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends(
            user1 TEXT,
            user2 TEXT,
            status BOOL,
            PRIMARY KEY (user1, user2)
        );
""")
seeddata = [('mikolajszywala', 'mikelarteta', 1), ('mikelarteta', 'ronniepickering', 1), ('auba', 'mikolajszywala', 1), ('kai', 'ronniepickering', 1), ('cliffburton', 'mikelarteta', 0), ('cliffburton', 'auba', 0), ('cliffburton', 'kai', 1)]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO users(user1, user2, status)
            VALUES (?, ?, ?)
        """, item)
    except:
        pass

#Make table for scheduling workouts on days of week
cursor.execute("""
    CREATE TABLE IF NOT EXISTS weeklyschedule(
        id INTEGER PRIMARY KEY,
        user TEXT,
        day TEXT,
        exercises TEXT,
        partners TEXT,
        starttime TEXT,
        endtime TEXT
    )
""")
seeddata = [('kai', 'Monday', 'benchpress, deadlift', 'ronniepickering', '19:30', '21:00'), ('kai', 'Wednesday', 'benchpress, deadlift', 'ronniepickering', '19:30', '21:00'), ('kai', 'Friday', 'benchpress, deadlift', 'ronniepickering', '19:30', '21:00'), ('kai', 'Tuesday', 'overhead press', 'cliffburton', '19:30', '21:00'), ('cliffburton', 'Thursday', 'squat', '', '05:40', '07:15'), ('ronniepickering', 'Tuesday', 'skullcrushers', 'mikelarteta,kai', '17:00', '19:00')]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO weeklyschedule(user, day, exercises, partners, starttime, endtime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, item)
    except:
        pass
connection.commit()
connection.close()