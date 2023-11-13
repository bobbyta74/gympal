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