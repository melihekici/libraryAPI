from flask import Flask, json, jsonify, request, make_response
from flask_restful import Api, Resource
from pymongo import MongoClient
from loginHelpers import *
from libraryCheckHelpers import *
from bookTransfer import *

app = Flask(__name__)
api = Api(app)

# Local MongoDB server
cluster = MongoClient("mongodb://localhost:27017/")

db = cluster['test']
books = db['books']
users = db['users']

def isNumeric(entry):
    try:
        float(entry)
        return True
    except:
        return False

def generateResponse(status, message):
    return jsonify({
        "status": status,
        "msg": message
    })

class Books(Resource):
    def post(self):
        postedData = request.get_json()
        validRequest = self.checkRequest(postedData)
        if(validRequest):
            bookName = postedData['name']
        else:
            return generateResponse(301, "name is missing")
        
        return generateResponse(200, f"Library has {self.getBookCount(bookName)} {bookName}")

    def getBookCount(self, bookName):
        try:
            book = books.find({'name': bookName})[0]['count']
        except:
            return 0

        return book
    
    def checkRequest(self, postedData):
        if(not ('name' in postedData)):
            return False
        else:
            return True

class AddBook(Resource):
    def post(self):
        postedData = request.get_json()
        validRequest = self.checkRequest(postedData)
        if(validRequest):
            bookName = postedData['name']
            bookCount = postedData['count']
        else:
            return generateResponse(301, "name or count is missing")
        
        return self.addBook(bookName, bookCount)
    
    def addBook(self, bookName, bookCount):
        try:
            oldCount = books.find({'name': bookName})[0]['count']
        except:
            books.insert_one({'name': bookName, 'count': max(0, bookCount)})
            books.find({'name': bookName})[0]['count']
            return generateResponse(200, f"Book {bookName} has been added, now library has {bookCount}")

        books.update(
            {'name': bookName},
            {'$set':{
                'count': max(0, bookCount + oldCount)
            }})
        
        return generateResponse(200, f"Book {bookName} has been added, now library has {bookCount + oldCount}")
    
    def checkRequest(self, postedData):
        if(not ('name' in postedData and 'count' in postedData)):
            return False
        elif(not isNumeric(postedData['count'])):
            return False
        else:
            return True

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        validRequest = self.checkRequest(postedData)

        if(validRequest):
            username = postedData['username']
            password = postedData['password']
        else:
            return generateResponse(301, "Username or password is missing")

        if(userExist(users, username)):
            return generateResponse(301, "This username is taken.")
        
        hashedPw = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert_one({
            'Username': username,
            'Password': hashedPw,
            'Books': []
        })

        return generateResponse(200, "Successfuly registered to the library API.")

    def checkRequest(self, postedData):
        if(not ('username' in postedData and 'password' in postedData)):
            return False
        else:
            return True

class RequestBook(Resource):
    def post(self):
        postedData = request.get_json()
        validRequest = self.checkRequest(postedData)
        if(validRequest):
            username = postedData['username']
            password = postedData['password']
            book = postedData['book']
        else:
            return generateResponse(301, "Username, password or book is missing")
        
        if(not verifyPw(users, username, password)):
            return generateResponse(301, "Wrong username or password")
        
        if(not bookAvailable(books, book)):
            return generateResponse(200, "The book you are searching for is not currently available in the library.")
        
        user = users.find({'Username': username})[0]
        if(userHaveIt(user, book)):
            return generateResponse(200, "You already have this book. You can not take it again.")

        requestBook.delay(username, book)
        return generateResponse(200, "Request has been taken")

    def checkRequest(self, postedData):
        if(not ('username' in postedData and 'password' in postedData and 'book' in postedData)):
            return False
        else:
            return True

class MyBooks(Resource):
    def post(self):
        postedData = request.get_json()
        validRequest = self.checkRequest(postedData)
        
        if(validRequest):
            username = postedData['username']
            password = postedData['password']
        else:
            return generateResponse(301, "Username or password is missing")
        
        if(not verifyPw(users, username, password)):
            return generateResponse(301, "Wrong username or password")
        
        return generateResponse(200, users.find({'Username': username})[0]['Books'])
        

    def checkRequest(self, postedData):
        if(not ('username' in postedData and 'password' in postedData)):
            return False
        else:
            return True       


api.add_resource(Books, '/book-count')
api.add_resource(AddBook, '/add-book')
api.add_resource(Register, '/register')
api.add_resource(RequestBook, '/request-book')
api.add_resource(MyBooks, '/my-books')

if(__name__ == '__main__'):
    app.run(host='0.0.0.0', debug=True)