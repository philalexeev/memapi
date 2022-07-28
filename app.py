from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = "admin"
api_password = "testadmin1"

def auth_protect(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if (
            auth
            and auth.username == api_username
            and auth.password == api_password
        ):
            return f(*args, **kwargs)
        return jsonify({ "error_message": "Authentication failed!"}), 403
    return decorated


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "sqlite_db"):
        g.sqlite_db.close()

@app.route('/members', methods=["GET"])
@auth_protect
def get_members():
    db = get_db()
    all_members_cur = db.execute("select * from members")
    all_members = all_members_cur.fetchall()

    all_members_data = []
    for member in all_members:
        all_members_data.append({
            "id": member["id"],
            "name": member["name"],
            "email": member["email"],
            "level": member["level"]
        })

    return jsonify(all_members_data)

@app.route('/member/<int:member_id>', methods=["GET"])
@auth_protect
def get_member(member_id):
    db = get_db()
    member_cur = db.execute(
        "select id, name, email, level from members where id = ?",
        [member_id]
    )
    member = member_cur.fetchone()

    return jsonify({
            "id": member["id"],
            "name": member["name"],
            "email": member["email"],
            "level": member["level"]
        })

@app.route('/member', methods=["POST"])
@auth_protect
def add_member():
    new_member_data = request.get_json()    # returns <dict>
    db = get_db()
    db.execute(
        "insert into members (name, email, level) values (?, ?, ?)",
        [
            new_member_data['name'],
            new_member_data['email'],
            new_member_data['level']
        ]
    )
    db.commit()

    new_member_cur = db.execute(
        "select id, name, email, level from members where name = ?",
        [new_member_data['name']]
    )
    new_member = new_member_cur.fetchone()

    return jsonify(
        {
            "id": new_member["id"],
            "name": new_member["name"],
            "email": new_member["email"],
            "level": new_member["level"]
        }
    )

@app.route('/member/<int:member_id>', methods=["PUT", "PATCH"])
@auth_protect
def edit_member(member_id):
    db = get_db()

    new_member = request.get_json()
    db.execute(
        "update members\
        set name = ?, email = ?, level = ?\
        where id = ?",
        [
            new_member["name"],
            new_member["email"],
            new_member["level"],
            member_id
        ]
    )
    db.commit()

    return jsonify(
        {
            "id": member_id,
            "name": new_member["name"],
            "email": new_member["email"],
            "level": new_member["level"]
        }
    )

@app.route('/member/<int:member_id>', methods=["DELETE"])
@auth_protect
def delete_member(member_id):
    db = get_db()
    db.execute(
        "delete from members where id = ?",
        [member_id]
    )
    db.commit()

    return f"Member with id {member_id} has been deleted"

if __name__ == "__main__":
    app.run(debug=True)