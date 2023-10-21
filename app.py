import flask, sqlite3

def initialise_db():
    connection = sqlite3.connect("users.db")
    cursor = connection.cursor()

    #Make table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gymbros(
            username TEXT,
            coords TEXT,
            membership TEXT,
            strengthlevel INTEGER,
            schedule TEXT,
            style TEXT
        )
    """)
    connection.commit()
    connection.close()
initialise_db()

@app.route("/")
def front():
    return flask.redirect("/static/userinfo.html")

@app.route("/userinfo", methods = ["GET"])
def userinfo():
    connection = sqlite3.connect("people.db")
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

