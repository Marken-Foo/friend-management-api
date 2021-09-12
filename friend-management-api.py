import re
import sqlite3

from flask import Flask, jsonify, request


DB_NAME = "users.db"
EMAIL_REGEX = re.compile(r"[\w\-\.]+@[\w\-]+(?:\.[\w]+)+")

app = Flask(__name__)


def connect_to_db(db_path=DB_NAME):
    con = sqlite3.connect(db_path)
    return con


def create_json_response(is_success=False, **kwargs):
    return jsonify({"success": is_success, **kwargs})


def is_email_valid(email_str):
    """Validate email address. Currently only checks against a simple regex.
    """
    match = EMAIL_REGEX.fullmatch(email_str)
    return match is not None


def are_users_friends(conn, email1, email2):
    cur = conn.cursor()
    cur.execute("SELECT * FROM friend "
        "INNER JOIN email AS e1 ON friend.email_id1 = e1.email_id "
        "INNER JOIN email AS e2 ON friend.email_id2 = e2.email_id "
        "WHERE e1.email = ? AND e2.email = ? "
        ";", (email1, email2)
    )
    res = cur.fetchone() is not None
    cur.close()
    return res


def are_users_blocking(conn, email1, email2):
    cur = conn.cursor()
    cur.execute("SELECT * FROM block "
        "INNER JOIN email AS e1 ON block.blocker_email_id = e1.email_id "
        "INNER JOIN email AS e2 ON block.blocked_email_id = e2.email_id "
        "WHERE e1.email = ? AND e2.email = ? "
        ";", (email1, email2)
    )
    res = cur.fetchone() is not None
    cur.close()
    return res


@app.post("/users")
def add_email():
    req = request.get_json()
    try:
        email = req["email"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email address received (JSON key should be 'email')"
        )
    if not is_email_valid(email):
        return create_json_response(is_success=False,
            error="Invalid email address received"
        )
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO email (email) VALUES (?);", (email,))
        conn.commit()
        return create_json_response(is_success=True)
    except sqlite3.IntegrityError as err:
        message = err.args[0]
        if "unique constraint" in message.lower():
            return create_json_response(is_success=False,
                error="Email already exists"
            )
        else:
            return create_json_response(is_success=False,
                error="Unexpected SQLite integrity error"
            )
    finally:
        conn.close()


@app.post("/friend")
def add_friends():
    req = request.get_json()
    try:
        emails = req["friends"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON key should be 'friends', "
            "email addresses should be in array value)"
        )
    if ((len(emails) < 2)
        or emails[0] == emails[1]
        or (not is_email_valid(emails[0]))
        or (not is_email_valid(emails[1]))
    ):
        return create_json_response(is_success=False,
            error="Two distinct valid email addresses required"
        )
    with connect_to_db() as conn:
        # if blocked, respond
        if are_users_blocking(conn, emails[0], emails[1]):
            return create_json_response(is_success=False,
                error="At least one user is blocking the other"
            )
        # if already friends, respond
        if are_users_friends(conn, emails[0], emails[1]):
            return create_json_response(is_success=False,
                error="Users are already friends"
            )
        else:
            try:
                cur = conn.cursor()
                cur.execute("INSERT INTO main.friend (email_id1, email_id2) "
                    "SELECT e1.email_id, e2.email_id "
                    "FROM email AS e1 "
                    "INNER JOIN email AS e2 "
                    "ON e1.email = ? AND e2.email = ? "
                    ";", (emails[0], emails[1])
                )
                conn.commit()
                return create_json_response(is_success=True)
            except sqlite3.IntegrityError as err:
                message = err.args[0]
                # We had checked for existing friend connection already
                return create_json_response(is_success=False,
                    error="Unexpected SQLite integrity error"
                )


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