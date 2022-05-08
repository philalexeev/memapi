from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/day")
def day():
    return render_template("day.html")

@app.route("/addfood")
def addfood():
    return render_template("addfood.html")