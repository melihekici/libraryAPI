
def bookAvailable(booksDB, requestedBook):
    """
    Checks if the requested book present in the library.

    Returns:
        True/False
    """
    book = booksDB.find({'name': requestedBook})
    if(book.count() == 0):
        return False
    elif(book[0]['count'] == 0):
        return False
    else:
        return True

def userHaveIt(user, requestedBook):
    """
    Checks if the user already have the requested book.
    
    Returns:
        True/False
    """
    if(requestedBook in user['Books']):
        return True
    else:
        return False