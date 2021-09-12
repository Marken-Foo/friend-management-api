import sqlite3

from flask import Flask, jsonify, request


DB_NAME = "users.db"

app = Flask(__name__)
conn_users = sqlite3.connect(DB_NAME)


@app.post("/users")
def add_email():
    # check if email
    # add to db and respond
    return "add email"


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