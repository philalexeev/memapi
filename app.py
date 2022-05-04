from crypt import methods
from flask import Flask, redirect, render_template, request, session, url_for, g
import sqlite3

app = Flask(__name__)

# setup app from config
app.config.from_pyfile('config.cfg')

# connect db to app
def connect_db():
    sql = sqlite3.connect("./database.db")
    sql.row_factory = sqlite3.Row   # replace tuples with dicts
    return sql

# get connected db
def get_db():
    if not hasattr(g, "sqlite3"):
        g.sqlite_db = connect_db()
    return g.sqlite_db

# close db connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

# simple route exmpl + set session tool (cookie)
@app.route("/", methods=["GET", "POST"])
def index():
    session["os"] = "linux"
    return "<h1>Flask Application</h1>"

# route with typed param (string below) and default value for this param
# + using session tool (cookie)
# + using template with params
@app.route("/greet", methods=["GET", "POST"], defaults={"name": "admin"})
@app.route("/greet/<string:name>", methods=["GET", "POST"])
def greet(name):
    if "os" in session:
        os_name = session["os"]
    else:
        os_name = "unknown os"

    return render_template(
        "greet.html",
        name=name,
        os_name=os_name,
        colored=True,
        specs=[
            ("ram", "16Gb"),
            ("processor", "intel core i5-3570"),
            ("ssd", "256Gb")
        ]
    )

# route with getting query params (needed import request module)
@app.route("/query")
def query():
    name = request.args.get("name")
    age = request.args.get("age")
    return f"<h1>Given name is {name} and the age is {age}</h1>"

# two routes below handle form
# and its processing with getting form fields values
# + using html templates
@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/processform", methods=["POST"])
def processform():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    return f"<h1>welcome, {name}! your email is {email} \
        and password is {password}, correct?</h1>"

# route with handling incoming json with post method
@app.route("/processjson", methods=["POST"])
def processjson():
    data = request.get_json()

    name = data["name"]
    age = data["age"]
    location = data["location"]

    return f"<h1>your name is {name}, the age is {age} \
        and you're in {location}.</h1>"

# the form route but handles get and post methods and redirects to another route
@app.route("/form2", methods=["GET", "POST"])
def form2():
    if request.method == "GET":
        return """
            <form
                action="/form2"
                method="post"
                enctype="multipart/form-data"
            >
                <input type="text" name="name" placeholder="name">
                <input type="text" name="age" placeholder="age">
                <button type="submit">submit</button>
            </form>
        """
    else:
        name = request.form["name"]
        age = request.form["age"]

        return redirect(url_for("greet", name=name, age=age))

@app.route("/table", methods=["POST", "GET"])
def table():
    if request.method == "GET":
        db = get_db()
        cur = db.execute("SELECT id, name, salary from Users")
        results = cur.fetchall()

        return render_template(
            "table.html",
            results=results
        )
    else:
        name = request.form["name"]
        salary = request.form["salary"]

        db = get_db()
        cur = db.execute(f"INSERT INTO Users (name, salary) VALUES (?, ?)", [name, salary])
        db.commit()

        return redirect("/table")

# the form for the database row inserting
@app.route("/dbform", methods=["GET", "POST"])
def dbform():
    if request.method == "GET":
        return """
            <form
                action="/table"
                method="post"
                enctype="multipart/form-data"
            >
                <input type="text" name="name" placeholder="name">
                <input type="text" name="salary" placeholder="salary">
                <button type="submit">submit</button>
            </form>
        """
    else:
        return redirect("/")