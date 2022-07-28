from flask import Flask

app = Flask(__name__)

app.route('/members', methods=["GET"])
def get_members():
    return "This returns all the members"

app.route('/member/<int:member_id>', methods=["GET"])
def get_member(member_id):
    return "This return the member by id"

app.route('/member', methods=["POST"])
def add_members():
    return "This adds a new member"

app.route('/member/<int:member_id>', methods=["PUT", "PATCH"])
def edit_member(member_id):
    return "This edits the member by id"

app.route('/member/<int:member_id>', methods=["DELETE"])
def delete_member():
    return "This removes a member by id"

if __name__ == "__main__":
    app.run(debug=True)