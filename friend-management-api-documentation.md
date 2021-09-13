# Friend management API documentation

## Add email to database

Add an email to the database.

JSON request should include user email in string parameter `email`.
```
{
  'email':'a@example.com'
}
```

Endpoint: `POST /users`

Response: `200`


## Create friend connection
Create a friend connection between two emails, if both are in the database. This is a symmetric relationship.

Endpoint: `POST /friend`

JSON request should include two emails as strings in array parameter `friends`.
```
{
  'friends':
    [
    'a@example.com',
    'b@example.com'
    ]
}
```

Response: `200`

Will fail if emails do not exist in the database, or if either email is blocking the other.

Sends JSON response with boolean parameter `success`, and if unsuccessful, a string parameter `error` explaining the error.


## Remove friend connection
Remove a friend connection between two emails.


JSON request should include two emails as strings in array parameter `friends`.
```
{
  'friends':
    [
    'a@example.com',
    'b@example.com'
    ]
}
```
Endpoint: `POST /unfriend`

Response: `200`

Will succeed even if emails are not in the database.

Sends JSON response with boolean parameter `success`, and if unsuccessful, a string parameter `error` explaining the error.


## Get friend list
Get the friend list of a user. Returns JSON with array of friends' emails and count of friends.

JSON request should include user email in string parameter `email`.
```
{
  'email':'a@example.com'
}
```
Endpoint `GET /friend_list`

Response: `200`

Will fail if provided email is not in database.

Sends JSON response with boolean parameter `success`, integer `count`, and array of strings `friends`. If unsuccessful, a string parameter `error` explaining the error.


## Get list of common friends
Get the list of common friends of two users and the total number.

JSON request should include two emails as strings in array parameter `friends`.
```
{
  friends:
    [
    'a@example.com',
    'b@example.com'
    ]
}
```
Endpoint: `GET /common_friends`

Response: `200`

Will fail if either provided email is not in database.

Sends JSON response with boolean parameter `success`, integer `count`, and array of strings `friends`. If unsuccessful, a string parameter `error` explaining the error.


## Subscribe one email to another
Subscribes one user to another to receieve notifications.

JSON request should include subscriber email as `requestor` and followed email as `target`.
```
{
  'requestor':'a@example.com',
  'target':'b@example.com'
}
```
Endpoint: `POST /subscribe`

Response: `200`

Will fail if either provided email is not in database, or if subscriber is blocking target.

Sends JSON response with boolean parameter `success`. If unsuccessful, a string parameter `error` explaining the error.


## Unsubscribe one email from another
Unsubscribes one user from another to stop receieving notifications.

JSON request should include subscriber email as `requestor` and followed email as `target`.
```
{
  'requestor':'a@example.com',
  'target':'b@example.com'
}
```
Endpoint: `POST /unsubscribe`

Response: `200`

Will succeed if either provided email is not in database.

Sends JSON response with boolean parameter `success`. If unsuccessful, a string parameter `error` explaining the error.


## Block one email by another
Blocks one user from another.

JSON request should include blocker email as `requestor` and blocked email as `target`.
```
{
  'requestor':'a@example.com',
  'target':'b@example.com'
}
```
Endpoint: `POST /block`

Response: `200`

Will fail if either provided email is not in database, or if blocker is friends with or subscribed to blocked email.

Sends JSON response with boolean parameter `success`. If unsuccessful, a string parameter `error` explaining the error.


## Unblock one email from another
Unblocks one user from another.

JSON request should include blocker email as `requestor` and blocked email as `target`.
```
{
  'requestor':'a@example.com',
  'target':'b@example.com'
}
```
Endpoint: `POST /unblock`

Response: `200`

Will succeed if either provided email is not in database.

Sends JSON response with boolean parameter `success`. If unsuccessful, a string parameter `error` explaining the error.


## Get list of notified users
Get list of users who will be notified of the message text, including emails mentioned in the text.

Users who will be notified are any subscribers, friends, and emails in the message text who are not blocking the sender.

JSON request should include sender email as `sender` and message text as `text` parameters.
```
{
  'sender': 'a@example.com',
  'text': 'Good morning b@example.com See you soon!'
}
```

Endpoint: `GET /notified`

Response: `200`

Sends JSON response with boolean parameter `success` and array of emails `recipients`. If unsuccessful, a string parameter `error` explaining the error.
