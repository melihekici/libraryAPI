# libraryAPI
Flask-REST-MondoDB-Celery

## Requirements
Python Packages:  
bcrypt  
celery==5.1.2
Flask  
Flask-RESTful  
pymongo  
redis  
redis-server  

Other:  
MongoDB Local

## Run:
Open two terminals, one for celery and one for web.py

First terminal -> celery -A bookTransfer worker -c 20 --loglevel=info
Second terminal -> python3 web.py


A Library API:
* Add book to library
* Remove book from library
* Register with username and password
* Take book from library (if available)

End Points:
### '/book-count'
request body: {  
  "name": (book-name)    
}

Returns the number of <book-name> available at Library.

### '/add-book'
request body: {  
  "name": (name of the book),  
  "count": (count to be added)  
}

Increases/decreases number of books available at library with given name.

### '/register'
request body: {  
  "username": (your username),  
  "password": (your password)  
}

Registers you to the API, required to take books from library.
If username you choose is taken, you will get a response accordingly

### '/request-book'
request body: {  
  "username": (your username),  
  "password": (your password),  
  "book": (name of the book you request)  
}

Returns a message that says your request is taken.
The function that will decide whether you will get the book or not runs asyncronously.


### '/my-books'
request body: {
  "username": (your username),  
  "password": (your password)
}

In Response body, returns an array that shows all of your books.
  
