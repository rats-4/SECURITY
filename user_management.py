import sqlite3 as sql
import time
import random


def insertUser(username, password, DoB):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users (username,password,dateOfBirth) VALUES (?,?,?)",
        (username, password, DoB),
    )
    con.commit()
    con.close()


def retrieveUser(username):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    con.close()
    if user:
        return user[0]  # Return the hashed password
    return None


def insertFeedback(feedback):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute(f"INSERT INTO feedback (feedback) VALUES ('{feedback}')")
    con.commit()
    con.close()


def listFeedback():
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    data = cur.execute("SELECT * FROM feedback").fetchall()
    con.close()
    f = open("templates/partials/success_feedback.html", "w")
    for row in data:
        f.write("<p>\n")
        f.write(f"{row[1]}\n")
        f.write("</p>\n")
    f.close()

def storeUserSecret(username, user_secret):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("UPDATE users SET totp_secret = ? WHERE username = ?", (user_secret, username))
    con.commit()
    con.close()

def retrieveUserSecret(username):
    con = sql.connect("database_files/database.db")
    cur = con.cursor()
    cur.execute("SELECT totp_secret FROM users WHERE username = ?", (username,))
    user_secret = cur.fetchone()
    con.close()
    if user_secret:
        return user_secret[0]  # Return the TOTP secret
    return None
