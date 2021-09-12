import re
import sqlite3

from flask import Flask, jsonify, request


DB_NAME = "users.db"
EMAIL_REGEX = re.compile(r"[\w\-\.]+@[\w\-]+(?:\.[\w]+)+")

app = Flask(__name__)


class SqlQueries:
    """Struct to hold SQL queries as text"""
    # check if user A is blocked by user B
    CHECK_IF_BLOCKING = '''SELECT * FROM block 
        INNER JOIN email AS e1 ON block.blocker_email_id = e1.email_id
        INNER JOIN email AS e2 ON block.blocked_email_id = e2.email_id
        WHERE e1.email = ? AND e2.email = ?
        ;
    '''
    
    # check if users are friends
    CHECK_IF_FRIENDS = '''SELECT * FROM friend
        INNER JOIN email AS e1 ON friend.email_id1 = e1.email_id
        INNER JOIN email AS e2 ON friend.email_id2 = e2.email_id
        WHERE (e1.email = ? AND e2.email = ?)
        OR (e2.email = ? AND e1.email = ?)
        ;
    '''
    
    # add email to database
    ADD_EMAIL = "INSERT INTO email (email) VALUES (?);"
    
    # check if email in database
    CHECK_IF_EXISTS = "SELECT * FROM email WHERE email.email = ?;"
    
    # establish friend connection
    ESTABLISH_FRIEND_CONNECTION = '''INSERT INTO friend (email_id1, email_id2)
        SELECT e1.email_id, e2.email_id
        FROM email AS e1
        INNER JOIN email AS e2
        ON e1.email = ? AND e2.email = ?
        ;
    '''
    
    # delete friend connection
    UNFRIEND = '''DELETE FROM friend
        WHERE (email_id1, email_id2) IN (
            SELECT email_id1, email_id2 FROM friend
            INNER JOIN email AS e1 ON friend.email_id1 = e1.email_id
            INNER JOIN email AS e2 ON friend.email_id2 = e2.email_id
            WHERE (e1.email = ? AND e2.email = ?) OR (e2.email = ? AND e1.email = ?)
        );
    '''
    
    # get friend list of user
    GET_FRIEND_LIST = '''SELECT e2.email FROM friend
        INNER JOIN email AS e1 ON friend.email_id1 = e1.email_id
        INNER JOIN email AS e2 ON friend.email_id2 = e2.email_id
        WHERE e1.email = ?
        UNION
        SELECT e1.email FROM friend
        INNER JOIN email AS e1 ON friend.email_id1 = e1.email_id
        INNER JOIN email AS e2 ON friend.email_id2 = e2.email_id
        WHERE e2.email = ?
        ;
    '''
    
    # subscribe user to target; subscriber is first, target is second
    SUBSCRIBE_USER_TO_TARGET = '''INSERT INTO subscription
        SELECT e1.email_id, e2.email_id
        FROM email AS e1
        INNER JOIN email AS e2
        ON e1.email = ? AND e2.email = ?
    '''
    
    # unsubscribe user from target; subscriber is first, target is second
    UNSUBSCRIBE_USER_FROM_TARGET = '''DELETE FROM subscription
        WHERE (subscriber_email_id, target_email_id) IN (
            SELECT subscriber_email_id, target_email_id FROM subscription
            INNER JOIN email AS e1 ON subscription.subscriber_email_id = e1.email_id
            INNER JOIN email AS e2 ON subscription.target_email_id = e2.email_id
            WHERE e1.email = ? AND e2.email = ?
        );
    '''


def connect_to_db(db_path=DB_NAME):
    con = sqlite3.connect(db_path)
    return con


def create_json_response(is_success=False, **kwargs):
    return jsonify({"success": is_success, **kwargs})


def respond_success():
    return create_json_response(is_success=True)


def respond_no_json_received():
    return create_json_response(is_success=False, error="No JSON received")


def respond_invalid_email_received():
    return create_json_response(is_success=False,
        error="Invalid email address received"
    )


def is_email_valid(email_str):
    """Validate email address. Currently only checks against a simple regex.
    """
    match = EMAIL_REGEX.fullmatch(email_str)
    return match is not None


def does_email_exist(conn, email):
    cur = conn.cursor()
    cur.execute(SqlQueries.CHECK_IF_EXISTS, (email,))
    res = cur.fetchone() is not None
    cur.close()
    return res


def are_users_friends(conn, email1, email2):
    cur = conn.cursor()
    cur.execute(SqlQueries.CHECK_IF_FRIENDS, (email1, email2, email1, email2)
    )
    res = cur.fetchone() is not None
    cur.close()
    return res


def are_users_blocking(conn, blocker, blocked):
    cur = conn.cursor()
    cur.execute(SqlQueries.CHECK_IF_BLOCKING, (blocker, blocked)
    )
    res = cur.fetchone() is not None
    cur.close()
    return res


def get_friend_list(conn, email):
    cur = conn.cursor()
    cur.execute(SqlQueries.GET_FRIEND_LIST, (email, email))
    friend_list = cur.fetchall()
    cur.close()
    return friend_list


@app.post("/users")
def add_email():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        email = req["email"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email address received (JSON key should be 'email')"
        )
    if not is_email_valid(email):
        return respond_invalid_email_received()
    try:
        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(SqlQueries.ADD_EMAIL, (email,))
        conn.commit()
        return respond_success()
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
    if req is None:
        return respond_no_json_received()
    try:
        emails = req["friends"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON key should be 'friends', "
            "email addresses should be in array value)"
        )
    # Take just first two emails from json array only if they are valid
    if ((len(emails) < 2) or emails[0] == emails[1]):
        return create_json_response(is_success=False,
            error="Two distinct valid email addresses required"
        )
    if (not is_email_valid(emails[0])) or (not is_email_valid(emails[1])):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        if are_users_blocking(conn, emails[0], emails[1]):
            return create_json_response(is_success=False,
                error="At least one user is blocking the other"
            )
        if are_users_friends(conn, emails[0], emails[1]):
            return create_json_response(is_success=False,
                error="Users are already friends"
            )
        else:
            try:
                cur = conn.cursor()
                cur.execute(
                    SqlQueries.ESTABLISH_FRIEND_CONNECTION,
                    (emails[0], emails[1]),
                )
                conn.commit()
                return respond_success()
            except sqlite3.IntegrityError as err:
                message = err.args[0]
                # We had checked for existing friend connection already
                return create_json_response(is_success=False,
                    error="Unexpected SQLite integrity error"
                )


@app.post("/unfriend")
def remove_friends():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        emails = req["friends"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON key should be 'friends', "
            "email addresses should be in array value)"
        )
    # Take just first two emails from json array only if they are valid
    if ((len(emails) < 2) or emails[0] == emails[1]):
        return create_json_response(is_success=False,
            error="Two distinct valid email addresses required"
        )
    if (not is_email_valid(emails[0])) or (not is_email_valid(emails[1])):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        cur = conn.cursor()
        cur.execute(SqlQueries.UNFRIEND, (emails[0], emails[1], emails[0], emails[1]))
        conn.commit()
        return respond_success()


@app.get("/friend_list")
def get_friends_of_user():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        email = req["email"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email address received (JSON key should be 'email')"
        )
    if not is_email_valid(email):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        if does_email_exist(conn, email):
            friend_list = get_friend_list(conn, email)
            return create_json_response(is_success=True,
                friends=friend_list,
                count=len(friend_list)
            )
        else:
            return create_json_response(is_success=False,
                error="Email does not exist"
            )


@app.get("/common_friends")
def get_common_friends():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        emails = req["friends"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON key should be 'friends', "
            "email addresses should be in array value)"
        )
    # Take just first two emails from json array only if they are valid
    if len(emails) < 2:
        return create_json_response(is_success=False,
            error="Two distinct valid email addresses required"
        )
    if (not is_email_valid(emails[0])) or (not is_email_valid(emails[1])):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        if (does_email_exist(conn, emails[0])
            and does_email_exist(conn, emails[1])
        ):
            mutual_friends = set(get_friend_list(conn, emails[0])).intersection(
                set(get_friend_list(conn, emails[1]))
            )
            return create_json_response(is_success=True,
                friends=list(mutual_friends),
                count=len(mutual_friends)
            )
        else:
            return create_json_response(is_success=False,
                error="One or both of the provided emails does not exist."
            )


@app.post("/subscribe")
def subscribe_requestor_to_target():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        req_email = req["requestor"]
        target_email = req["target"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON keys should be 'requestor'"
            "and 'target' for respective email addresses)"
        )
    if (not is_email_valid(req_email)) or (not is_email_valid(target_email)):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        if not (does_email_exist(conn, req_email)
            and does_email_exist(conn, target_email)
        ):
            return create_json_response(is_success=False,
                error="One or both of the provided emails does not exist."
            )
        # if requestor has blocked target, do not create subscription
        elif are_users_blocking(conn, blocker=req_email, blocked=target_email):
            return create_json_response(is_success=False,
                error="Requestor has blocked target, please unblock first"
            )
        else:
            try:
                cur = conn.cursor()
                cur.execute(SqlQueries.SUBSCRIBE_USER_TO_TARGET,
                    (req_email, target_email)
                )
                conn.commit()
                return respond_success()
            except sqlite3.IntegrityError as err:
                message = err.args[0]
                if "unique constraint" in message.lower():
                    return create_json_response(is_success=False,
                        error="User already subscribed"
                    )
                else:
                    return create_json_response(is_success=False,
                        error="Unexpected SQLite integrity error"
                    )


@app.post("/unsubscribe")
def unsubscribe_requestor_from_target():
    req = request.get_json()
    if req is None:
        return respond_no_json_received()
    try:
        req_email = req["requestor"]
        target_email = req["target"]
    except KeyError:
        return create_json_response(is_success=False,
            error="No email addresses received (JSON keys should be 'requestor'"
            "and 'target' for respective email addresses)"
        )
    if (not is_email_valid(req_email)) or (not is_email_valid(target_email)):
        return respond_invalid_email_received()
    with connect_to_db() as conn:
        cur = conn.cursor()
        cur.execute(SqlQueries.UNSUBSCRIBE_USER_FROM_TARGET,
            (req_email, target_email)
        )
        conn.commit()
        return respond_success()


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