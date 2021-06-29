import time
from libraryCheckHelpers import *
from flask import jsonify
from pymongo import MongoClient
from celery import Celery
import random

cel = Celery('bookTransfer',
            broker='redis://localhost',
            backend='redis://localhost')

# Local MongoDB server
cluster = MongoClient("mongodb://localhost:27017/")

db = cluster['test']
books = db['books']
users = db['users']

@cel.task()
def requestBook(username, requestedBook):
    time.sleep(random.randint(3, 5))
    if(not bookAvailable(books, requestedBook)):
        # return generateResponse(200, "The book you are searching for is not currently available in the library.")
        print("Not available")
        return
    
    user = users.find({'Username': username})[0]
    if(userHaveIt(user, requestedBook)):
        # return generateResponse(200, "You already have this book. You can not take it again.")
        print("Not available")
        return

        
    # return books.find({'name': bookName})[0]['count']
    giveBook(users, books, user, requestedBook)
    returnBook.delay(user['Username'], requestedBook)


def generateResponse(status, message):
    return jsonify({
        "status": status,
        "msg": message
    })

@cel.task()
def returnBook(username, returnedBook):
    time.sleep(random.randint(5, 10))

    user = users.find({'Username': username})[0]
    bookList = user['Books']
    bookList.remove(returnedBook)
    # Remove book from the users inventory
    users.update(
        {'Username': user['Username']},
        {'$set':{'Books': bookList}})
    
    # Increment book count in library
    oldCount = books.find({'name': returnedBook})[0]['count']
    books.update(
        {'name': returnedBook},
        {'$set':{'count': oldCount + 1}}
    )
    print("You have returned the book")
    print(user['Books'])

def giveBook(usersDB, booksDB, user, requestedBook):
    # Add book to the users inventory
    usersDB.update(
        {'Username': user['Username']},
        {'$set':{'Books': user['Books'] + [requestedBook]}})
    
    # Deduct book count from library inventory
    oldCount = booksDB.find({'name': requestedBook})[0]['count']
    booksDB.update(
        {'name': requestedBook},
        {'$set':{'count': oldCount - 1}}
    )

    print("You have received the book")