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
("ronniepickering", "2b88761a800fc84917bdea1e12bb7f368258829d80efa62c89dae5b423dda3f2", "52.20387 20.96515", "artis", "bodybuilding", 125, 125, 125, 125, "Monday,Tuesday,Wednesday", 31250, 547),
("mudwizard", "2bbd1e6451bc95f414be665c80a4f8ab69896929364816b830ed0a3cfaf4af9a", "52.23122 20.95108", "zdrofit", "powerlifting", 300, 200, 175, 125, "Monday,Tuesday,Wednesday,Thursday", 60000, 912),
("ozzyosbourne", "f91d49d7b81a4c46acb562c75e5189cfa40a22cfc0c68f261f71c50d0da3f7d7","52.24737 21.01481", "zdrofit", "powerlifting", 150, 140, 100, 80, "Monday,Wednesday,Friday", 36725, 408),
("mikolajszywala", "4f62a2e90dc4f4bb829722aaee5cbfd2f6e28ba18ab2c3051ef4b26428d37da0", "52.21791 21.07875", "artis", "bodybuilding", 190, 160, 125, 70, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday", 49050, 3360),
("auba", "71d63a1db9e724081d49f0bdd39cb24eca751d4b45ecc2cbb0af6e7edb604b56","52.22417 21.00796", "artis", "bodybuilding", 100, 100, 100, 100, "Monday,Wednesday,Friday,Sunday", 28000, 1072),
("ron", "b8cfbefe5fc598d0eaea7386995ef20b537371c328fd0ff938cacc79be00c410", "52.27947 21.11608", "cityfit", "crossfit", 25, 128, 21, 57, "Monday,Tuesday,Wednesday,Thursday,Friday,Saturday,Sunday", 16170, 559),
('donaldduck', 'ca528fa2989ab225db689a4b9be794f1596a283ee25b20317c9f6be4cbb507c7', '52.16576 21.08251', 'calypso', 'olympic', 300, 250, 20, 15, 'Friday,Saturday,Sunday', 55575, 746),
("arsenewenger", "9737210380399a58488a1a2baca7decd942717db863f658da0b53af4447a2a63", "52.22035 21.04087", "artis", "bodybuilding", 200, 150, 130, 85, "Monday,Tuesday,Thursday", 0, 0), 
('clifford', '3a5176fee097d3dce160dd0c436ca870399eed162e0a1b8163c42c20a79ed977', '52.23271 21.01853', 'artis', 'bodybuilding', 95, 86, 60, 40, 'Monday,Wednesday,Friday', 1597, 75), 
('cliffburton', '184098fac5c126873855e7ce025235d6349ea680f51073e281c057c37bd52abf', '52.24963 21.23084', 'artis', 'bodybuilding', 180, 165, 135, 75, 'Wednesday,Saturday,Sunday', 0, 0),
('szermierz', 'c3ae9839f150fffa2db8ce6ac5c26437c8e8178c4000072d13c5c5c076c3f888', '52.18808 20.98865', 'calypso', 'olympic', 130, 125, 90, 45, 'Tuesday,Thursday,Saturday', 1940, 35)
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
seeddata = [('mikolajszywala', 'arsenewenger', 1), ('arsenewenger', 'ronniepickering', 1), ('auba', 'mikolajszywala', 1), ('clifford', 'ronniepickering', 1), ('cliffburton', 'arsenewenger', 0), ('cliffburton', 'auba', 0), ('cliffburton', 'clifford', 1), ('leroyjenkins', 'clifford', 0), ('mikolajszywala', 'cliffburton', 1), ('mikolajszywala', 'ronniepickering', 1)]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO friends(user1, user2, status)
            VALUES (?, ?, ?)
        """, item)
    except:
        pass

#Make table for scheduling workouts on days of week
cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts(
        id INTEGER PRIMARY KEY,
        user TEXT,
        day TEXT,
        exercises TEXT,
        partners TEXT,
        starttime TEXT,
        endtime TEXT
    )
""")
seeddata = [(1, 'clifford', 'Monday', 'benchpress, deadlift', '', '19:30', '21:00'), (2, 'clifford', 'Wednesday', 'benchpress, deadlift', 'ronniepickering', '19:30', '21:00'), (3, 'clifford', 'Friday', 'benchpress, deadlift', '', '19:30', '21:00'), (4, 'clifford', 'Tuesday', 'overhead press', 'cliffburton', '19:30', '21:00'), (5, 'cliffburton', 'Thursday', 'squat', '', '05:40', '07:15'), (6, 'ronniepickering', 'Tuesday', 'skullcrushers', 'arsenewenger,clifford', '17:00', '19:00'), (7, 'mikolajszywala', 'Monday', 'benchpress, overhead', 'ronniepickering,auba,arsenewenger,cliffburton', '19:00', '20:00'), (8, 'mikolajszywala', 'Wednesday', 'benchpress, overhead', 'auba,arsenewenger', '19:00', '20:00'), (9, 'mikolajszywala', 'Friday', 'benchpress, overhead', 'ronniepickering,auba,arsenewenger,cliffburton', '19:00', '20:00'), (10, 'mikolajszywala', 'Tuesday', 'squat', '', '07:00', '08:00'), (11, 'mikolajszywala', 'Thursday', 'squat', '', '07:00', '08:00')]
for item in seeddata:
    try:
        cursor.execute("""
            INSERT INTO workouts(user, day, exercises, partners, starttime, endtime)
            VALUES (?, ?, ?, ?, ?, ?)
        """, item)
    except:
        pass
connection.commit()
connection.close()