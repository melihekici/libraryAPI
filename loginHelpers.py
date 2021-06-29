import bcrypt

def userExist(usersDB, username):
    """
    Checks if username exist in given MongoDB.

    Returns:
        True/False
    """
    if(usersDB.find({'Username': username}).count() == 0):
        return False
    else:
        return True

def verifyPw(usersDB, username, password):
    """
    Verifies if username and password matches in given MongoDB.
    """
    if(not userExist(usersDB, username)):
        return False
    
    hashedPw = usersDB.find({'Username': username})[0]['Password']
    if(bcrypt.hashpw(password.encode('utf8'), hashedPw) != hashedPw):
        return False
    
    return True




