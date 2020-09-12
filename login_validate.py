import sqlite3

def check_password(hashed_password, user_password):
    return hashed_password == user_password

def validate(username, password, identity):
    con = sqlite3.connect('database.db')
    completion = False
    if username=='administrator@lionstate.edu' and password=="iamad":
        completion=True
    elif identity=='Student':
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM student")
            rows = cur.fetchall()
            for row in rows:
                dbUser = row[0]
                dbPass = row[1]
                if dbUser==username:
                    completion=check_password(dbPass, password)
    elif identity =='Professor':
        with con:
            cur = con.cursor()
            cur.execute("SELECT * FROM Professor")
            rows = cur.fetchall()
            for row in rows:
                dbUser = row[0]
                dbPass = row[1]
                if dbUser==username:
                    completion=check_password(dbPass, password)
    con.close()
    return (completion)

