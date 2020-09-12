from flask import Flask, render_template, redirect, url_for, request
import sqlite3

def create_assignment(course, section, assignment_type, number, details):
    complete=False
    connection = sqlite3.connect("database.db")

    if assignment_type == 'Homework':
        connection.execute("INSERT INTO Homework (course_id, sec_no, hw_no, hw_details) values (?,?,?,?);",
                           (course, section, number, details))
        connection.execute(""" INSERT INTO Homework_grades (student_email,course_id, sec_no, hw_no, grade)
                                SELECT student_email,?,?,?, null
                                FROM Homework_grades H
                                WHERE H.course_id=? AND H.sec_no=?;""", (course, section, number, course, section))

        connection.commit()
        complete = True
    if assignment_type == 'Exam':
        connection.execute("INSERT INTO Exams (course_id, sec_no, exam_no, exam_details) values (?,?,?,?);",
                           (course, section, number, details))
        connection.execute(""" INSERT INTO Exam_grades (student_email,course_id, sec_no, exam_no, grades)
                                            SELECT student_email,?,?,?, null
                                            FROM Exam_grades H
                                            WHERE H.course_id=? AND H.sec_no=?;""",
                           (course, section, number, course, section))

        connection.commit()
        complete = True
    return(complete)