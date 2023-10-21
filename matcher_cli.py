import flask, sqlite3

connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

#Make table containing all users' data
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT,
        coords TEXT,
        membership TEXT,
        style TEXT,
        biglifttotal INTEGER,
        schedule TEXT
    )
""")
connection.commit()

#Insert existing/seed data (because there are so many criteria I'm not gonna do it manually every time lol)
seeddata = [
    ("ronniepickering", "52.203877248629254, 20.965159296723883", "artis", "bodybuilding", 500, "monday,tuesday,wednesday"),
    ("mudwizard", "52.23122168568795, 20.95108306546127", "zdrofit", "powerlifting", 800, "monday,tuesday,wednesday,thursday"),
    ("ozzyosbourne", "52.24737393593506, 21.014812388173574", "totalfitness", "bodybuilding", 650, "monday,wednesday,friday"),
    ("mikolajszywala", "52.15182950616367, 21.06355143963846", "artis", "bodybuilding", 100, "monday,tuesday,wednesday,thursday,friday,saturday")
]
for item in seeddata:
    cursor.execute("""
        INSERT INTO users(username, coords, membership, style, biglifttotal, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
    """, item)

#Proto-login
#Enter username, then check if already registered
username = input("Enter username: ")
result = cursor.execute("""
    SELECT * FROM users
    WHERE username = ?
""", [ username ]).fetchone()


if result is None:
    #Username not registered yet
    #Enter new user info
    coords = input("Enter coordinates: ")
    membership = input("What gym are you a member of? ")
    style = input("What is your workout style? Pick one from bodybuilding, crossfit, powerlifting or olympic: ")
    big_lift_total = int(input("What is the total weight (in kg) you can lift in deadlift, squat, benchpress and overhead press? "))
    schedule = input("When do you go to the gym? Enter days of the week separated by commas: ")
    cursor.execute("""
        INSERT INTO users(username, coords, membership, style, biglifttotal, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [username, coords, membership, style, big_lift_total, schedule])
    connection.commit()
    print("Data entered successfully")
else:
    #Find gymbros that satisfy criteria
    #Remember the record that matches the input username has already been queried in lines 33-37

    #Convert query result into dictionary 
    column_names = ["username", "coords", "membership", "style", "biglifttotal", "schedule"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}
    possible_gymbros = cursor.execute("""
    SELECT * FROM users
    WHERE membership = ? AND style = ? AND username <> ?
    """, [ result["membership"], result["style"], result["username"] ]).fetchall()
    print(possible_gymbros)

connection.close()

