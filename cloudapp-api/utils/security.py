

#define pepper as constant value here

def generateIdToken(userId):
    """
    Generate a token to uniquely identify a user

    generates a user secret which is saved in the database and 
    computes the user token using 'id+':'+random_secret+':'+hash(pepper+id+':'+random_secret)

    :param userId: user id used to refer to the user

    :returns: 2 values - user secret, whole token 
    """

    return ""

def saveUser(userId, userSecret):
    """
    Registers the user in the database as a unique party member

    :param userId: user id used to refer to the user
    :param userSecret: computed user unique secret

    :returns: success/failure @add format
    """

    #will call a DatabaseUtilities method to interact with db for real

    return ""

def checkUser(userToken):
    """
    Checks if a given userToken represents an legitimate party room member

    :param userToken: value saved on the user device in a cookie

    :returns: if verified - success, else - failure
    """

    return ""