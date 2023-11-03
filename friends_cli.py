import sqlite3
connection = sqlite3.connect("gymbros.db")
cursor = connection.cursor()

def initialise_db():
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

keepgoing = True
while keepgoing:
    connection = sqlite3.connect("gymbros.db")
    cursor = connection.cursor()
    #Check if they have any requests
    currentuser = input("Enter username: ")
    requests = cursor.execute("""
        SELECT * FROM friends
        WHERE user2 = ? AND status = 0
    """, [currentuser]).fetchall()
    for request in requests:
        connection = sqlite3.connect("gymbros.db")
        cursor = connection.cursor()
        acceptmaybe = input(f"Accept friend request from {request[0]}?")
        if acceptmaybe == "yes":
            cursor.execute(f"""
                UPDATE friends
                SET status = 1
                WHERE user1 = ? AND user2 = ?
            """, [request[0], currentuser])
            connection.commit()


    hopefullyfriendo = input("Who do you want to befriend? ")
    def friendship_exists(twodlist, a, b):
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
    print(friendship_exists(result, currentuser, hopefullyfriendo)[1])
    if friendship_exists(result, currentuser, hopefullyfriendo)[0]: 
        if friendship_exists(result, currentuser, hopefullyfriendo)[1] == True:
            print("Friendship already exists")
        else:
            print("Friend request already made")
    else:
        cursor.execute("INSERT INTO friends(user1, user2, status) VALUES (?, ?, 0)", [currentuser, hopefullyfriendo])
    connection.commit()
    
    keepgoing = input("\nAdd new friend? ")
    if keepgoing == "no":
        break
result = cursor.execute("SELECT * FROM friends").fetchall()
print(result)
cursor.execute("DROP TABLE IF EXISTS friends")
connection.commit()
connection.close()