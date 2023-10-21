import flask, sqlite3

connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

#Make table containing all users' data
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        username TEXT PRIMARY KEY,
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
    ("mikolajszywala", "52.15182950616367, 21.06355143963846", "artis", "bodybuilding", 100, "monday,tuesday,wednesday,thursday,friday,saturday"),
    ("aubameyang", "52.224173181636694, 21.007969059592277", "artis", "bodybuilding", 350, "monday,wednesday,friday,sunday")
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

    #Convert query result from tuple into dictionary 
    #E.g. {username: ronniepickering,
    #      coords: 51.1421749201, 20.148172144,
    #      etc.}
    column_names = ["username", "coords", "membership", "style", "biglifttotal", "schedule"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}

    #List possible gymbros sorted by different factors:
    sorting_factor = input("""How do you want to sort your matches?
Enter 'big lift total' to sort by how similar your strength level is
Enter 'location' to sort by how close you are physically
Enter 'schedule' to sort by the amount of scheduled days you have in common:
    """)
    #Splice condition into query based on chosen factor
    if sorting_factor == "big lift total":
        #Find difference between big lift total of user and others, sort ascending (from most to least similar)
        possible_gymbros = cursor.execute("""
            SELECT *, Abs(biglifttotal - ?) AS strengthdiff FROM users
            WHERE membership = ? AND style = ? AND username <> ?
            ORDER BY strengthdiff
        """, [ result["biglifttotal"], result["membership"], result["style"], result["username"] ]).fetchall()
    elif sorting_factor == "location":
        #Haversine formula
        possible_gymbros = cursor.execute("""
        SELECT * FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
    elif sorting_factor == "schedule":
        #Have to manipulate strings to compare here, can't be done in SQL only :(((
        def schedulecoverage(myschedule, otherschedule):
            #MAJOR ALGORITHMIC THINKING INSIDE, MENTION IN WRITEUP
            #Returns how well myschedule is covered by otherschedule (%)
            #This literally took me 2.5hrs to formulate lol
            #Turn both comma-separated strings into lists
            a = myschedule.split(",")
            origlength = len(a)
            b = otherschedule.split(",")
            #Try to subtract every day in person b's schedule from person a's schedule
            #If person a's schedule is completely within person b's schedule, there is nothing left in array a at the end (0% remaining, 100% coverage)
            #If they don't match at all, no days will be removed from array a (100% remaining, 0% coverage)
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

