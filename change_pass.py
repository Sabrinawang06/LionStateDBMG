from flask import Flask, render_template, redirect, url_for, request
import sqlite3

def change_password(identity,id, old, new, new2):
    if identity=='student':
        connection = sqlite3.connect('database.db')
        completion = False
        oldpass=connection.execute('select password from student where email=?;', (id,))
        p=oldpass.fetchall()
        for row in p :
            if old==(row[0]) and new==new2:
                print(row[0])
                connection.execute('UPDATE student Set password=? where email=?;',(new,id))
                completion=True
                connection.commit()

    if identity=='Professor':
        connection = sqlite3.connect('database.db')
        completion = False
        oldpass=connection.execute('select password from professor where email=?;', (id,))
        p = oldpass.fetchall()
        for row in p:
            if old == (row[0]) and new == new2:
                print(row[0])
                connection.execute('UPDATE professor Set password=? where email=?;', (new, id))
                completion = True
                connection.commit()



    return (completion)

