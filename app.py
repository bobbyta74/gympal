import flask, sqlite3

#Make user database
def initialise_db():
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
            schedule TEXT,
            monthsvolume INTEGER,
            monthstimespent INTEGER
        )
    """)
    #Make table linking users as friends
    #User1 is the friendor, user2 is the friendee
    #status set as 0/false when friend request made, changed to 1/true when accepted by other user
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends(
            user1 TEXT,
            user2 TEXT,
            status BOOL,
            PRIMARY KEY (user1, user2)
        );
    """)

    connection.commit()
    connection.close()

initialise_db()

app = flask.Flask(__name__)
app.secret_key = 'x\xed9\xa4P\xf9\x1b\xea\xb5\x94\xc4\x90}\x7f\xd6\xb3'

@app.route("/")
def front():
    return flask.redirect("/static/login.html")

@app.route("/login", methods = ["GET"])
def login():
    #Log in as existing user

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    #Request username from titlebar (e.g. login?username=ronniepickering)
    username = flask.request.args.get("username")
    password = flask.request.args.get("password")

    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()
    if result != None and password == result[1]:
        #Save username between routes (for use in other sites)
        flask.session["username"] = username
        return {
            "type": "success"
        }
    else:
        return {
            "type": "failure"
        }


from geopy.geocoders import Nominatim
@app.route("/register", methods = ["GET"])
def register():
    #Register new user

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    #Input addresses like /userinfo?username=bob&style=epic
    username = flask.request.args.get("username")
    password = flask.request.args.get("pwd")
    membership = flask.request.args.get("membership")
    style = flask.request.args.get("style")
    deadlift = flask.request.args.get("deadlift")
    squat = flask.request.args.get("squat")
    bench = flask.request.args.get("bench")
    overhead = flask.request.args.get("overhead")
    schedule = flask.request.args.get("schedule")

    #Convert address to standardised 5dp (accurate to individual house) coordinates
    address = flask.request.args.get("address")
    geolocator = Nominatim(user_agent="gympal")
    location = geolocator.geocode(address)
    try:
        coords = str(round(location.latitude, 5)) + " " + str(round(location.longitude, 5))
        print(coords)
    except:
        return {
            "error": True,
            "errortype": "invalidaddress"
        }

    #Check if username is registered already
    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()

    #If username exists in database, pause registration 
    if result:
        return {
            "error": True,
            "errortype": "usernametaken"
        }
    #Otherwise enter user's details into database
    else:
        #Insert flask.requests into new database record
        cursor.execute("""
            INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule, monthsvolume, monthstimespent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
        """, [username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule])
        connection.commit()
        connection.close()
        #Save username between routes (for use in other sites)
        flask.session["username"] = username
        return {
            "error": False
        }

@app.route("/username", methods=["GET"])
def username():
    if "username" in flask.session:
        return {
            "username": flask.session["username"]
        }
    else:
        return {
            "username": False
        }

@app.route("/logout")
def logout():
    del flask.session["username"]
    return flask.redirect("/static/login.html")

import geopy.distance
@app.route("/matches", methods=["GET"])
def matches():
    #Find gymbros that satisfy criteria

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    #Get current user's record for values of sorting criteria
    username = flask.session["username"]
    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()

    #Convert query result from tuple into dictionary (easier to read/remmenber key names than indexes)
    #Don't need month's volume and time spent, so not included
    column_names = ["username", "password", "coords", "membership", "style", "deadlift", "squat", "bench", "overhead", "schedule"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}

    sorting_factor = flask.request.args.get("crit")
    possible_gymbros = "none"

    #Splice condition into query based on chosen factor
    if sorting_factor == "[Select criterion]":
        possible_gymbros = cursor.execute("""
        SELECT username, coords, membership, style, deadlift, squat, bench, overhead, schedule
        FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        ORDER BY username
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
    #strength
    elif sorting_factor == "Difference in big lift total (kg)":
        #Find difference between big lift total of user and others, sort ascending (from most to least similar)
        possible_gymbros = cursor.execute("""
            SELECT username, coords, membership, style, deadlift, squat, bench, overhead, schedule, Abs(deadlift+squat+bench+overhead - ?) AS strengthdiff 
            FROM users
            WHERE membership = ? AND style = ? AND username <> ?
            ORDER BY strengthdiff
        """, [ (result["deadlift"]+result["squat"]+result["bench"]+result["overhead"]), result["membership"], result["style"], username ]).fetchall()
    #location
    elif sorting_factor == "Distance from you (km)":
        queried_gymbros = cursor.execute("""
        SELECT username, coords, membership, style, deadlift, squat, bench, overhead, schedule 
        FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
        possible_gymbros = []
        for gymbro in queried_gymbros:
            #Get the coordinates of user and gymbro
            usercoords = result["coords"]
            gymbrocoords = gymbro[1]
            usercoords = usercoords.split()[0], usercoords.split()[1]
            gymbrocoords = gymbrocoords.split()[0], gymbrocoords.split()[1]
            #Add distance field to query results
            gymbro_as_list = list(gymbro)
            gymbro_as_list.append(round(geopy.distance.geodesic(usercoords, gymbrocoords).km, 3))
            possible_gymbros.append(gymbro_as_list)
            #Sort the query result by distance
            possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=False)
    #schedule
    elif sorting_factor == "Schedule coverage (%)":
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
        queried_gymbros = cursor.execute("""
        SELECT username, coords, membership, style, deadlift, squat, bench, overhead, schedule
        FROM users
        WHERE membership = ? AND style = ? AND username <> ?
        """, [ result["membership"], result["style"], result["username"] ]).fetchall()
        possible_gymbros = []
        for gymbro in queried_gymbros:
            #Add schedule coverage to each gymbro's record tuple (in the query result, not in the actual table)
            gymbro_as_list = list(gymbro)
            gymbro_as_list.append(schedulecoverage(result["schedule"], gymbro[8]))
            possible_gymbros.append(gymbro_as_list)
        #Sort the query result by gymbros' schedule coverages
        possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=True)
    
    return {
        "matches": possible_gymbros
    }

@app.route("/friendrequest", methods=["GET"])
def friendrequest():
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    hopefullygymbro = flask.request.args.get("requested")

    #Avoid redundant friend requests
    def bothinrecord(twodlist, a, b):
        for sublist in twodlist:
            if a in sublist and b in sublist:
                if sublist[2] == 1:
                    #Friendship accepted
                    return [True, True]
                elif sublist[2] == 0:
                    #Friendship requested
                    return [True, False]
        #No friendship
        return [False, False]

    result = cursor.execute("SELECT * FROM friends").fetchall()
    if bothinrecord(result, currentuser, hopefullygymbro)[0]: 
        if bothinrecord(result, currentuser, hopefullygymbro)[1] == True:
            return {
                "outcome": "You're already gymbros with this dude, goober :|"
            }
        else:
            return {
                "outcome": "You requested this gymbro already, silly :|"
            }
    else:
        cursor.execute("INSERT INTO friends(user1, user2, status) VALUES (?, ?, 0)", [currentuser, hopefullygymbro])
        connection.commit()
        connection.close()
        return {
            "outcome": "Gymbro requested! Radical, my dude!"
        }

import json
@app.route("/workout", methods=["GET"])
def workout():
    #Update records and month's volume 

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    sessionrecords = json.loads(flask.request.args.get("records"))
    sessionvolume = int(flask.request.args.get("volume"))
    sessionduration = int(flask.request.args.get("timespent"))

    #Get current user's record to add data
    username = flask.session["username"]
    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()
    #Convert to dictionary for easier access
    column_names = ["username", "password", "coords", "membership", "style", "deadlift", "squat", "bench", "overhead", "schedule", "monthsvolume", "monthstimespent"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}

    #Update PR if new
    newrecords = ""
    for lift in ["deadlift", "squat", "bench", "overhead"]:
        sessionrecords[lift] = int(sessionrecords[lift])
        if sessionrecords[lift] > result[lift]:
            cursor.execute(f"""
                UPDATE users
                SET {lift} = ?
                WHERE username = ?
            """, [ sessionrecords[lift], username ])
            newrecords += lift + ", " 

    #Add session volume and time spent to month's values
    cursor.execute("""
        UPDATE users
        SET monthsvolume = ?, monthstimespent = ?
        WHERE username = ?
    """, [ (result["monthsvolume"] + sessionvolume), (result["monthstimespent"] + sessionduration), username ])

    connection.commit()
    connection.close()

    return {
        "new records": newrecords[:-2]
    }

@app.route("/leaderboards", methods=["GET"])
def leaderboards():
    #Show all users ordered by chosen criterion
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    criterion = flask.request.args.get("criterion")
    if criterion != "username":
        result = cursor.execute(f"""
            SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, monthsvolume, monthstimespent
            FROM users
            ORDER BY {criterion} DESC
        """).fetchall()
    else:
        #Sort alphabetically by default
        result = cursor.execute(f"""
            SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, monthsvolume, monthstimespent
            FROM users
            ORDER BY {criterion}
        """).fetchall()

    return {
        "data": result
    }