#Deprecated DO NOT RUN
import flask, sqlite3

connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

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

    #Convert query result from tuple into dictionary 
    #E.g. {username: ronniepickering,
    #      coords: 51.1421749201, 20.148172144,
    #      etc.}
    column_names = ["username", "password", "coords", "membership", "style", "deadlift", "squat", "bench", "overhead", "schedule"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}

    #List possible gymbros sorted by different factors:
    sorting_factor = input("""How do you want to sort your matches?
Enter 'strength' to sort by how similar your strength level is
Enter 'location' to sort by how close you are physically
Enter 'schedule' to sort by the amount of scheduled days you have in common:
    """)
    #Splice condition into query based on chosen factor
    if sorting_factor == "strength":
        #Find difference between big lift total of user and others, sort ascending (from most to least similar)
        possible_gymbros = cursor.execute("""
            SELECT *, Abs(deadlift+squat+bench+overhead - ?) AS strengthdiff FROM users
            WHERE membership = ? AND style = ? AND username <> ?
            ORDER BY strengthdiff
        """, [ (int(result["deadlift"])+int(result["squat"])+int(result["bench"])+int(result["overhead"])), result["membership"], result["style"], username ]).fetchall()
    elif sorting_factor == "location":
        #Haversine formula
        possible_gymbros = cursor.execute("""
        SELECT * FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
    elif sorting_factor == "schedule":
        #Have to manipulate strings to compare here, can't be done in SQL only :(((
        def schedulecoverage(myschedule, otherschedule):
            #Turn both comma-separated strings into lists
            a = myschedule.split(",")
            origlength = len(a)
            b = otherschedule.split(",")
            #Try to subtract every day in person b's schedule from person a's schedule, if every day is left then there is no coverage
            for day in b:
                try:
                    a.remove(day)
                except:
                    pass
            return int(100 - (len(a)/origlength*100))
        #All possible gymbros (unsorted)
        possible_gymbros = cursor.execute("""
        SELECT * FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
        for gymbro in possible_gymbros:
            #Add schedule coverage to each gymbro's record tuple (in the query result, not in the actual table)
            gymbro += (schedulecoverage(result["schedule"], gymbro[5]),)
        #Sort the query result by gymbros' schedule coverages
        possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=False)

            
    print(possible_gymbros)

connection.close()

