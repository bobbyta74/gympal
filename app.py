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

@app.route("/")
def front():
    return flask.redirect("/static/login.html")

@app.route("/login", methods = ["GET"])
def login():
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
        return {
            "type": "success"
        }
    else:
        return {
            "type": "failure"
        }


@app.route("/register", methods = ["GET"])
def register():
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
        return {
            "usernametaken": False
        }