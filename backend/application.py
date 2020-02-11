import os

from flask import Flask, request, session, render_template, jsonify
from flask_session import Session
from flask_cors import CORS, cross_origin
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import psycopg2
import requests

# template_folder='../bookexplorer/public/
app = Flask(__name__)
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
CORS(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
conn = psycopg2.connect(os.getenv("DATABASE_URL"), sslmode='require')
db = scoped_session(sessionmaker(bind=engine))
#CORS(conn)

@app.route("/")
@cross_origin()
def index():
    return "Hello World"

@app.route("/register")
@cross_origin()
def registering():
    username = request.args.get("username")
    password = request.args.get("password")
    #try to add user to database, return fail if unable
    try:
        db.execute("INSERT INTO registered_users (username, password) VALUES (:username, :password)", 
        {"username": username, "password": password})

        db.commit() 
    except exc.SQLAlchemyError:
        return "failure"
    return "success"

@app.route("/namecheck")
@cross_origin()
def namecheck():
    username = request.args.get("username")
    if db.execute("SELECT username FROM registered_users WHERE username=:username", {"username": username}).rowcount == 1:
        return ({"user": username, "exists": "true"})
    else:
        return ({"exists": "false"}) 

@app.route("/loggingin")
@cross_origin()
def loggingin():
    username = request.args.get("username")
    password = request.args.get("password")
    if db.execute("SELECT username FROM registered_users WHERE username=:username AND password=:password", {"username": username, "password": password}).rowcount == 1:
        return ({"user": username, "loggedin": "true"})
    else:
        return ({"user": username, "loggedin": "false"}) 

@app.route("/booksearch")
@cross_origin()
def booksearch():
    book = request.args.get("book")
    option = request.args.get("option")
    if option == "Author":
        out_book = db.execute("SELECT * FROM library WHERE author LIKE :book", {"book": "%" + book + "%"}).fetchall()
        data = jsonify({'result': [dict(row) for row in out_book]})
        return data
    elif option == "Title":
        out_book = db.execute("SELECT * FROM library WHERE title LIKE :book", {"book": "%" + book + "%"}).fetchall()
        data = jsonify({'result': [dict(row) for row in out_book]})
        return data
    elif option == "Year":
        out_book = db.execute("SELECT * FROM library WHERE CAST(year as TEXT) LIKE :book", {"book": "%" + book + "%"}).fetchall()
        data = jsonify({'result': [dict(row) for row in out_book]})
        return data
    elif option == "ISBN":
        out_book = db.execute("SELECT * FROM library WHERE isbn LIKE :book", {"book":"%" + book + "%"}).fetchall()
        data = jsonify({'result': [dict(row) for row in out_book]})
        return data

@app.route("/goodread")
@cross_origin()
def goodread():
    # key = "swIxMzw2BAh2FK5fXd3PSg"
    url = "https://www.goodreads.com/book/review_counts?key=swIxMzw2BAh2FK5fXd3PSg&isbns="
    isbns = request.args.get("isbn")
    test = url + isbns + "&format=json"
    r = requests.get(url + isbns + "&format=json")
    if r.ok:
        return jsonify({"goodread": r.json(), "status": "good"}) 
    else:
        return jsonify({"status": "bad"}) 