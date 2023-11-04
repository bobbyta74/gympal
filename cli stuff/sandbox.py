import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

criterion = "deadlift"
result = cursor.execute(f"""
            SELECT username, deadlift, squat, bench, overhead, (deadlift + squat) AS lowerbody, (bench + overhead) AS upperbody, (deadlift + squat + bench + overhead) AS bigtotal, monthsvolume, monthstimespent
            FROM users
            ORDER BY {criterion} DESC
        """).fetchall()

scale = "friendsonly"
currentuser = "mikolajszywala"
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
    result = friendsleaderboard
#Otherwise just show the whole leaderboard

print(friendsleaderboard)