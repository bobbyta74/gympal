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

#Proto-login
#Enter username, then check if already registered
username = input("Enter username: ")
result = cursor.execute("""
    SELECT * FROM users
    WHERE username = ?
""", [ username ]).fetchone()


#Username not registered yet
#Enter new user info
if result is None:
    coords = input("Enter coordinates: ")
    membership = input("What gym are you a member of? ")
    style = input("What is your workout style? Pick one from bodybuilding, crossfit, powerlifting or olympic: ")
    biglifttotal = int(input("What is the total weight (in kg) you can lift in deadlift, squat, benchpress and overhead press? "))
    schedule = input("When do you go to the gym? Enter days of the week separated by commas: ")
    cursor.execute("""
        INSERT INTO users(username, coords, membership, style, biglifttotal, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [username, coords, membership, style, biglifttotal, schedule])
    connection.commit()
    print("Data entered successfully")
else:
    print("Already registered")

connection.close()

