from flask import Flask, render_template, request, g
import sqlite3
from datetime import datetime

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

@app.route("/", methods=["POST", "GET"])
def home():
    db = get_db()

    if request.method == "POST":
        date = request.form["date"]
        dt = datetime.strptime(date, "%Y-%m-%d")
        database_date = datetime.strftime(dt, "%Y%m%d")
        db.execute(
            "insert into log_date (entry_date) values (?)", [database_date]
        )
        db.commit()

    cur = db.execute("select entry_date from log_date order by entry_date desc")
    results = cur.fetchall()

    date_results = []

    for item in results:
        item_date = datetime.strptime(str(item["entry_date"]), "%Y%m%d")
        single_date = datetime.strftime(item_date, "%B %d, %Y")
        date_results.append((single_date, str(item["entry_date"])))

    return render_template("home.html", results=date_results)

@app.route("/day/<date>", methods=["GET", "POST"])
def day(date):
    db = get_db()

    cur = db.execute(
        "select id, entry_date from log_date where entry_date = ?",
        [date]
    )
    date_results = cur.fetchone()

    if request.method == "POST":
        db.execute(
            "insert into food_date (food_id, log_date_id) values (?, ?)",
            [request.form["food-select"], date_results["id"]]
        )
        db.commit()

    r_date = datetime.strptime(str(date_results["entry_date"]), "%Y%m%d")
    pretty_date = datetime.strftime(r_date, "%B %d, %Y")

    food_cur = db.execute("select id, name from food")
    food_results = food_cur.fetchall()

    log_cur = db.execute(
        "select food.name, food.protein, food.carbohydrates, food.fat,\
        food.calories from log_date join food_date on food_date.log_date_id = \
        log_date.id join food on food.id = food_date.food_id \
        where log_date.entry_date = ?",
        [date]
    )
    log_results = log_cur.fetchall()

    totals = {}
    totals["protein"] = 0
    totals["carbohydrates"] = 0
    totals["fat"] = 0
    totals["calories"] = 0

    for food in log_results:
        totals["protein"] += food["protein"]
        totals["carbohydrates"] += food["carbohydrates"]
        totals["fat"] += food["fat"]
        totals["calories"] += food["calories"]
    
    return render_template(
        "day.html",
        short_date=date_results["entry_date"],
        date=pretty_date,
        food_list=food_results,
        log_results=log_results,
        total=totals
    )

@app.route("/addfood", methods=["GET", "POST"])
def addfood():
    db = get_db()

    if request.method == "POST":
        name = request.form["food_name"]
        protein = int(request.form["protein"])
        carbohydrates = int(request.form["carbohydrates"])
        fat = int(request.form["fat"])
        calories = protein * 4 + carbohydrates * 4 + fat * 9

        db.execute("insert into food \
            (name, protein, carbohydrates, fat, calories) \
            values (?,?,?,?,?)", \
            [name, protein, carbohydrates, fat, calories])
        db.commit()
    
    cur = db.execute("select name, protein, carbohydrates, fat, calories from food")
    results = cur.fetchall()
    
    return render_template("addfood.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)