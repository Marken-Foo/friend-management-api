import sqlite3

from flask import Flask, jsonify, request


DB_NAME = "users.db"

app = Flask(__name__)


def connect_to_db(db_path=DB_NAME):
    con = sqlite3.connect(db_path)
    return con


@app.post("/users")
def add_email():
    req = request.get_json()
    try:
        email = req["email"]
    except KeyError:
        return jsonify({"success": False, "error": "No email address received"})
    # should also check if email is valid
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO email (email) VALUES (?);", (email,))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError as err:
        message = err.args[0]
        if "not null" in message.lower():
            return jsonify({"success": False, "error": "Null value for email received"})
        elif "unique constraint" in message.lower():
            return jsonify({"success": False, "error": "Email already exists"})
        else:
            return jsonify({"success": False, "error": "Unexpected SQLite integrity error"})
    finally:
        conn.close()
    # add to db and respond"


@app.post("/friend")
def add_friends():
    # check length is 2, check if are emails, if both in db
    # if blocked, respond
    # if already friends, respond
    # else update db and respond
    return "add friends"


@app.post("/unfriend")
def remove_friends():
    # check length is 2, check if are emails, if both in db
    # if not friends, respond
    # else update db and respond
    return "remove friends"


@app.get("/friend_list")
def get_friends_of_user():
    # check if is email
    # if not in db, respond
    # else generate friends list from db and respond
    return "friendlist"


@app.get("/common_friends")
def get_common_friends():
    # check if length 2, if are emails, if both in db
    # generate common friends list from db
    # respond (including count, if successful)
    return "common friends"


@app.post("/subscribe")
def subscribe_requestor_to_target():
    # check if are emails, if both in db
    # if requestor has blocked target, respond
    # if requestor has already subscribed to target, respond
    # else update db and respond
    return "subscribe"


@app.post("/unsubscribe")
def unsubscribe_requestor_from_target():
    # check if are emails, if both in db
    # if requestor is not subscribed to target, respond
    # else update db and respond
    return "unsubscribe"


@app.post("/block")
def block_target_by_requestor():
    # check for requestor and target, check if emails
    # if requestor has already blocked target, respond
    # if requestor is friend with target, respond
    # if requestor is subscribed to target, respond
    # update db
    # respond
    return "block"


@app.get("/notified")
def get_recipients_of_update():
    # check if sender is email, in db
    # search text for emails
    # if text contains emails, check if in db
    # get friends from db
    # get subscribers from db
    # get blocked from db
    # respond
    return "notified"