import flask, sqlite3

#Make and seed user database
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
            biglifttotal INTEGER,
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
    cursor = connecion.cursor()

    #Input addresses like /userinfo?username=bob&style=epic
    username = flask.request.args.get("username")
    style = flask.request.args.get("style")

    result = cursor.execute("""
        SELECT * FROM gymbros
        WHERE username = ?
    """, [username])

    if result is None:
        return "unregistered"