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
            volume INTEGER,
            timespent INTEGER
        )
    """)

    #Make table linking users as friends
    #user1 is the requester, user2 is the accepter/rejecter
    #status set as 0/false while friend request unaccepted, changed to 1/true when accepted by other user
    #Composite primary key line 35 to avoid duplicate records of the same 2 friends
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends(
            user1 TEXT,
            user2 TEXT,
            status BOOL,
            PRIMARY KEY (user1, user2)
        );
    """)

    #Make table containing details of individual scheduled workouts
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
    connection.commit()
    connection.close()

initialise_db()

app = flask.Flask(__name__)
app.secret_key = 'x\xed9\xa4P\xf9\x1b\xea\xb5\x94\xc4\x90}\x7f\xd6\xb3'

@app.route("/")
def front():
    return flask.redirect("/static/login.html")

import hashlib
def encrypt(pwd):
    pwd_bytes = pwd.encode("utf-8")
    myhash = hashlib.sha256()
    myhash.update(pwd_bytes)
    pwd_encrypted = myhash.hexdigest()
    return pwd_encrypted

#login.html
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
        #Save username between routes (for use on other pages)
        flask.session["username"] = username
        return {
            "type": "success"
        }
    else:
        return {
            "type": "failure"
        }

#register.html
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
        #Format coords as space-separated string (e.g. "3.45675 78.34532")
        coords = str(round(location.latitude, 5)) + " " + str(round(location.longitude, 5))
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
            INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule, volume, timespent)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0)
        """, [username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule])
        connection.commit()
        connection.close()
        #Save username between routes (for use in other sites)
        flask.session["username"] = username
        return {
            "error": False
        }

#Every page once logged in
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

#profile.html and settings.html
from geopy.geocoders import Nominatim
@app.route("/userdetails", methods=["GET"])
def userdetails():
    #Return details of current user
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()
    username = flask.session["username"]
    geolocator = Nominatim(user_agent="gympal")

    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [username]).fetchone()
    result = list(result)
    result[2] = str(geolocator.reverse(result[2].split()))
    #Hide password
    result.remove(result[1])
    return {
        "userdetails": result
    }

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
    #Don't need volume and time spent, so not included
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
        """, [ result["membership"], result["style"], result["username"] ]).fetchall() #Outputs a list of tuples, each tuple represents a potential gymbro
        possible_gymbros = [] #Make new 2D list to store gymbros as lists, not tuples
        for gymbro in queried_gymbros: #Iterate through potential gymbros
            #Get the coordinates of user and gymbro
            usercoords = result["coords"] #Coordinates of current user
            gymbrocoords = gymbro[1] #Coordinates of potential gymbro
            #Convert coordinates from space-separated string to tuple form to use in geopy distance function
            usercoords = usercoords.split()[0], usercoords.split()[1]
            gymbrocoords = gymbrocoords.split()[0], gymbrocoords.split()[1]

            gymbro_as_list = list(gymbro) #Convert potential gymbro from tuple form to list because can't append to tuple
            gymbro_as_list.append(round(geopy.distance.geodesic(usercoords, gymbrocoords).km, 3)) #Add to potential gymbro (list) the distance between them and the current user (3dp)
            possible_gymbros.append(gymbro_as_list) #Add potential gymbro (list) to 2D list of gymbros
            possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=False) #Sort 2D list of gymbros by distance (last item in 1D list)
    
    #schedule
    elif sorting_factor == "Schedule coverage (%)":
       #Returns how much of myschedule is included in otherschedule (e.g. "mon, tue, wed" is 67% covered in "mon, tue, fri")
       def schedulecoverage(myschedule, otherschedule):
           #Turn both comma-separated strings into lists
           a = myschedule.split(",")
           origlength = len(a) #Count initial length of myschedule (to be used in later calculation)
           b = otherschedule.split(",")


           #Remove days from myschedule that are covered by otherschedule
               #If every day is left then there is no coverage, if no days are left then coverage = 100%
           for day in b:
               #try/except used to avoid errors removing items that aren't in list (e.g. "thu" from ["mon", "wed", "fri"])
               try:
                   a.remove(day)
               except:
                   pass
           #Return proportion of days in common (days that were removed) to total days in myschedule
           return int(100 - (len(a)/origlength*100))


       queried_gymbros = cursor.execute("""
       SELECT username, coords, membership, style, deadlift, squat, bench, overhead, schedule
       FROM users
       WHERE membership = ? AND style = ? AND username <> ?
       """, [ result["membership"], result["style"], result["username"] ]).fetchall()
       possible_gymbros = []
       for gymbro in queried_gymbros:
           #Add schedule coverage to each gymbro's record tuple (in the query result, not in the actual table)
           gymbro_as_list = list(gymbro) #Convert gymbro from tuple to list (so can append data)
           potential_gymbro_schedule = gymbro[8] #gymbro[8] corresponds to potential gymbro's schedule
           #Calculate coverage between current user and potential gymbro
           gymbro_as_list.append(schedulecoverage(result["schedule"], potential_gymbro_schedule))
           #Add gymbro (with added schedule coverage) to list of possible gymbros
           possible_gymbros.append(gymbro_as_list)
       #Sort gymbros by descending schedule coverage (schedule coverage is last item in each gymbro_as_list)
       possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=True)
    
    return {
        "matches": possible_gymbros
    }

#FRIENDS
@app.route("/requestfriend", methods=["GET"])
def requestfriend():
    #Let current user request gymbro
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    hopefullygymbro = flask.request.args.get("requested")

    #Import the function from bothinrecord.py to avoid redundant friend requests (request/friend already exists)
    from bothinrecord import bothinrecord

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

@app.route("/getfriendreqs", methods=["GET"])
def getfriendreqs():
    #Check if user has received any friend requests
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]

    #Get the requester from unconfirmed requests of the current user
    friendrequests = cursor.execute("""
        SELECT user1 FROM friends
        WHERE user2 = ? AND status = 0
    """, [currentuser]).fetchall()

    return {
        "data": friendrequests
    }

@app.route("/processfriendreq", methods=["GET"])
def processfriendreq():
    #Accept or reject friend request in db
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    requester = flask.request.args.get("from")
    actiontype = flask.request.args.get("type")
    if actiontype == "accept":
        cursor.execute("""
            UPDATE friends
            SET status = 1
            WHERE user1 = ? AND user2 = ?
        """, [requester, currentuser])
    else:
        cursor.execute("""
            DELETE FROM friends
            WHERE user1 = ? AND user2 = ?
        """, [requester, currentuser])
    connection.commit()
    connection.close()
    return '', 204

@app.route("/getfriends", methods=["GET"])
def getfriends():
    #Let current user request gymbro
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    #Import the function from bothinrecord.py to check if ppl are friends
    from bothinrecord import bothinrecord

    friendslist = []
    userstable = cursor.execute("SELECT * FROM users").fetchall()
    friendstable = cursor.execute("SELECT * FROM friends").fetchall()

    #If request/friendship exists AND is friendship
    for user in userstable:
        if bothinrecord(friendstable, currentuser, user[0]) == [True, True] and user[0] != currentuser:
            friendslist.append(user[0])
    return {
        "friends": friendslist
    }

            

import json
@app.route("/workout", methods=["GET"])
def workout():
    #Update records and total volume 

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    #sessionrecords is a dictionary of the biggest lifts of the current session in every category (e.g. "deadlift": 95, "squat": 80)
    sessionrecords = json.loads(flask.request.args.get("records")) #Convert JSON string back into dictionary 
                                                                    #(couldn't send dictionary as a parameter so had to convert to JSON)
    sessionvolume = int(flask.request.args.get("volume"))
    sessionduration = int(flask.request.args.get("timespent"))

    #Get current user's record to add data
    username = flask.session["username"]
    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()
    #Convert to dictionary to make references more understandable (i.e. result["volume"] instead of result[5])
    column_names = ["username", "password", "coords", "membership", "style", "deadlift", "squat", "bench", "overhead", "schedule", "volume", "timespent"]
    result = {column_names[i]: result[i] for i in range(len(column_names))} #make dictionary joining corresponding key:value pairs from 2 lists

    #Update personal record if new
    newrecords = "" #output string of lift categories in which new records were set (e.g. "new records in: deadlift, benchpress")
    for exercise in ["deadlift", "squat", "bench", "overhead"]:
        sessionrecords[exercise] = int(sessionrecords[exercise])
        if sessionrecords[exercise] > result[exercise]: #compare record lift in category from current session to all-time record
            cursor.execute(f"""
                UPDATE users
                SET {exercise} = ?
                WHERE username = ?
            """, [ sessionrecords[exercise], username ]) #if greater than the all-time record, the current session record is the new all-time record
            newrecords += exercise + ", " #add current lift category to output (e.g. if the new record is deadlift, "deadlift" is added to string of new records)

    #Add session volume and time spent to month's values
    cursor.execute("""
        UPDATE users
        SET volume = ?, timespent = ?
        WHERE username = ?
    """, [ (result["volume"] + sessionvolume), (result["timespent"] + sessionduration), username ])

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
            SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, volume, timespent
            FROM users
            ORDER BY {criterion} DESC
        """).fetchall()
    else:
        #Sort alphabetically by default
        result = cursor.execute(f"""
            SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, volume, timespent
            FROM users
            ORDER BY {criterion}
        """).fetchall()

    #Limit to friends only if friends-only leaderboard chosen
    scale = flask.request.args.get("scale")
    currentuser = flask.session["username"]
    if scale == "friendsonly":
        friendsleaderboard = []
        #Get all friendships - both those initiated by the user and by someone else 
        userandfriends = cursor.execute("""
            SELECT user1
            FROM friends
            WHERE user2 = ? AND status = 1
        """, [currentuser]).fetchall() + cursor.execute("""
            SELECT user2
            FROM friends
            WHERE user1 = ? AND status = 1
        """, [currentuser]).fetchall()
        userandfriends = list(record[0] for record in userandfriends)
        userandfriends.append(currentuser)
        #For every person in the leaderboard, check if they're in the user's friends list (queried above)
        #If they are then add them to a new leaderboard list
        #Because stupid bloody python is incapable of deleting items from the original list that don't match the requirements
        for record in result:
            if record[0] in userandfriends:
                friendsleaderboard.append(record)
        return {
            "data": friendsleaderboard
        }
    #Otherwise just show the whole leaderboard
    else:
        return {
            "data": result
        }

@app.route("/getschedule")
def getschedule():
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()
    currentuser = flask.session["username"]

    scheduleobj = {}
    for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        daysworkouts = cursor.execute("""
            SELECT id, user, exercises, partners, starttime, endtime
            FROM workouts
            WHERE day = ? AND (user = ? OR partners LIKE ?)
            ORDER BY starttime
        """, [day, currentuser, f"%{currentuser}%"]).fetchall()
        scheduleobj[day] = daysworkouts
    return {
        #Dictionary with 2D list of workout tuples for each day
        "schedule": scheduleobj,
        "username": currentuser
    }

@app.route("/setschedule")
def setschedule():
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    days = flask.request.args.get("days").split(",")
    exercises = flask.request.args.get("exercises")
    partners = flask.request.args.get("partners")
    starttime = flask.request.args.get("start")
    endtime = flask.request.args.get("end")


    #Can schedule same exercise for multiple days
    for day in days:
        try:
            cursor.execute("""
            INSERT INTO workouts(user, day, exercises, partners, starttime, endtime)
            VALUES (?, ?, ?, ?, ?, ?)
            """, [currentuser, day, exercises, partners, starttime, endtime])
            connection.commit()
        except:
            connection.close()
            return {
                "data": "Error"
            }
    connection.close()
    return {
        "data": "Success!"
    }

@app.route("/removefromschedule")
def removefromschedule():
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    currentuser = flask.session["username"]
    workoutid = flask.request.args.get("workoutid")

    workout = cursor.execute("""
        SELECT * FROM workouts
        WHERE id = ?
    """, [workoutid]).fetchone()
    workout = list(workout)
    organisedbyuser = False
    #Check if organiser is user or someone else
    if workout[1] == currentuser:
        organisedbyuser = True
    else:
        organisedbyuser = False

    #If current user organised workout, let them delete it
    if organisedbyuser:
        cursor.execute("""
            DELETE FROM workouts
            WHERE id = ?
        """, [workoutid])
    #If not, unsubscribe only current user from that workout
    #So that organiser doesn't lose whole workout
    else:
        #Avoid awkward leftover commas
        #E.g. a,b,c -> a,,c
        #User to delete is either at start/middle of list, or at end 
        #E.g. to delete "a" from "a,b,c", "a," will be removed
        # But to delete "c" from "a,b,c", ",c" will be removed
        if workout[4] == workout[4].replace(currentuser + ",", ""):
            workout[4] = workout[4].replace("," + currentuser, "")
        else:
            workout[4] = workout[4].replace(currentuser + ",", "")
        #Neither of the 2 above will work if current user is the only partner, but this will
        workout[4] = workout[4].replace(currentuser, "")
        cursor.execute("""
            UPDATE workouts
            SET partners = ?
            WHERE id = ?
        """, [workout[4], workoutid])
        
    connection.commit()
    connection.close()
    return {
        "data": workout[4]
    }