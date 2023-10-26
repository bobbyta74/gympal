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
            schedule TEXT
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


@app.route("/register", methods = ["GET"])
def register():
    #Register new user

    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()

    #Input addresses like /userinfo?username=bob&style=epic
    username = flask.request.args.get("username")
    password = flask.request.args.get("pwd")
    coords = flask.request.args.get("coords")
    membership = flask.request.args.get("membership")
    style = flask.request.args.get("style")
    deadlift = flask.request.args.get("deadlift")
    squat = flask.request.args.get("squat")
    bench = flask.request.args.get("bench")
    overhead = flask.request.args.get("overhead")
    schedule = flask.request.args.get("schedule")

    #Check if username is registered already
    result = cursor.execute("""
        SELECT * FROM users
        WHERE username = ?
    """, [ username ]).fetchone()

    #If username exists in database, pause registration 
    if result:
        return {
            "usernametaken": True
        }
    #Otherwise enter user's details into database
    else:
        #Insert flask.requests into new database record
        cursor.execute("""
            INSERT INTO users(username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [username, password, coords, membership, style, deadlift, squat, bench, overhead, schedule])
        connection.commit()
        connection.close()
        #Save username between routes (for use in other sites)
        flask.session["username"] = username
        return {
            "usernametaken": False
        }

@app.route("/homepage", methods = ["GET"])
def homepage():
    return {
        "username": flask.session["username"]
    }

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
    column_names = ["username", "password", "coords", "membership", "style", "deadlift", "squat", "bench", "overhead", "schedule"]
    result = {column_names[i]: result[i] for i in range(len(column_names))}

    sorting_factor = flask.request.args.get("crit")
    possible_gymbros = "none"

    #Splice condition into query based on chosen factor
    if sorting_factor == "strength":
        #Find difference between big lift total of user and others, sort ascending (from most to least similar)
        possible_gymbros = cursor.execute("""
            SELECT *, Abs(deadlift+squat+bench+overhead - ?) AS strengthdiff FROM users
            WHERE membership = ? AND style = ? AND username <> ?
            ORDER BY strengthdiff
        """, [ (result["deadlift"]+result["squat"]+result["bench"]+result["overhead"]), result["membership"], result["style"], username ]).fetchall()
    elif sorting_factor == "location":
        #INSERT HAVERSINE FORMULA HERE
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
            gymbro += (schedulecoverage(result["schedule"], gymbro[9]),)
        #Sort the query result by gymbros' schedule coverages
        possible_gymbros = sorted(possible_gymbros, key=lambda x: x[-1], reverse=False)
    
    return {
        "matches": possible_gymbros
    }