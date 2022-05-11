from flask import Flask, render_template, request, g
import sqlite3

app = Flask(__name__)

# connect db to app
def connect_db():
    sql = sqlite3.connect("./food_log.db")
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

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/day")
def day():
    return render_template("day.html")

@app.route("/addfood", methods=['get', 'post'])
def addfood():
    if request.method == 'post':
        return render_template("addfood.html")
    else:
        form_fields = {
            "name": request.form["food_name"],
            "protein": request.form["protein"],
            "carbohydrates": request.form["carbohydrates"],
            "fat": request.form["fat"],
            "calories": request.form["calories"] 
        }
        return f"<h1>name: {form_fields['name']},\
            protein: {form_fields['protein']},\
            ch: {form_fields['carbohydrates']},\
            fat: {form_fields['fat']},\
            cl: {form_fields['calories']}</h1>"