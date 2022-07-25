from flask import Flask, render_template, g, request, session, redirect, url_for
from database import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)

# close db connection
@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

def get_current_user():
    user_result = None

    if "user" in session:
        user = session["user"]

        db = get_db()
        user_cur = db.execute(
            "select * from users where name = ?", [user]
        )
        user_result = user_cur.fetchone()

    return user_result

@app.route("/")
def home():
    user = get_current_user()
    db = get_db()

    questions_cur = db.execute(
        "select\
            questions.id,\
            questions.question_text,\
            askers.name as asker,\
            experts.name as expert\
        from questions\
        join users as askers on askers.id = questions.asked_by_id\
        join users as experts on experts.id = questions.expert_id\
        where questions.answer_text is not null"
    )
    answered_questions = questions_cur.fetchall()

    return render_template("home.html", user=user, questions=answered_questions)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        db = get_db()
        user_cur = db.execute(
            "select * from users where name = ?", [request.form["username"]]
        )
        user_result = user_cur.fetchone()
        
        if check_password_hash(
            user_result["password"], request.form["password"]
        ):
            session["user"] = user_result["name"]
            return redirect(url_for("home"))
        else:
            return "<h1 style='color:red;'>the password is incorrect</h1>"
    return render_template("login.html")

@app.route("/register", methods=["POST", "GET"])
def register():
    if request.method == "POST":
        db = get_db()

        existing_user_cur = db.execute(
            "select * from users where name = ?",
            [request.form['username']]
        )
        existing_user = existing_user_cur.fetchone()

        if existing_user:
            return render_template("register.html", error="User already exists")

        hashed_password = generate_password_hash(
            request.form["password"],
            method="sha256"
        )
        db.execute(
            "insert into users (name, password, expert, admin)\
            values (?, ?, ?, ?)", [
                request.form["username"],
                hashed_password,
                0,
                0
            ]
        )
        db.commit()

        session["name"] = request.form["username"]

        return redirect(url_for("home"))
    return render_template("register.html")

@app.route("/ask", methods=["GET", "POST"])
def ask():
    user = get_current_user()

    if not user:
        return redirect(url_for("login"))

    db = get_db()

    if (request.method == "POST"):
        db.execute(
            "insert into questions (question_text, asked_by_id, expert_id)\
            values (?, ?, ?)",
            [request.form['question'], user['id'], request.form['expert']]
        )
        db.commit()

        return redirect(url_for("ask"))

    experts_cur = db.execute(
        "select id, name from users where expert = 1"
    )
    experts = experts_cur.fetchall()

    return render_template("ask.html", user=user, experts=experts)

@app.route("/answer/<question_id>", methods=['GET', 'POST'])
def answer(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    db = get_db()

    if request.method == "POST":
        db.execute(
            "update questions set answer_text = ? where id = ?",
            [request.form['answer'], question_id]
        )
        db.commit()
        return redirect(url_for("unanswered"))

    question_cur = db.execute(
        "select id, question_text from questions where id = ?",
        [question_id]
    )
    question = question_cur.fetchone()

    return render_template("answer.html", user=user, question=question)

@app.route("/question/<question_id>")
def question(question_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    db = get_db()

    question_cur = db.execute(
        "select\
            questions.question_text,\
            questions.answer_text,\
            askers.name as asker,\
            experts.name as expert\
        from questions\
        join users as askers on askers.id = questions.asked_by_id\
        join users as experts on experts.id = questions.expert_id\
        where questions.id = ?",
        [question_id]
    )
    question_result = question_cur.fetchone()

    return render_template("question.html", user=user, question=question_result)

@app.route("/unanswered")
def unanswered():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))
    
    if user["expert"] == 0:
        return redirect(url_for("home"))

    db = get_db()
    questions = db.execute(
        "select questions.id, questions.question_text, users.name\
        from questions\
        join users on users.id = questions.asked_by_id\
        where questions.answer_text is null and questions.expert_id = ?",
        [user['id']]
    )

    return render_template("unanswered.html", user=user, questions=questions)

@app.route("/users")
def users():
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if user["admin"] == 0:
        return redirect(url_for("home"))

    db = get_db()
    user_cur = db.execute(
        "select id, name, expert, admin from users"
    )
    users_result = user_cur.fetchall()

    return render_template("users.html", user=user, users=users_result)

@app.route('/promote/<user_id>')
def promote(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for("login"))

    if user["admin"] == 0:
        return redirect(url_for("home"))

    db = get_db()
    db.execute(
        "update users set expert = iif(expert == 0, 1, 0) where id = ?",
        [user_id]
    )
    db.commit()
    return redirect(url_for("users"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)