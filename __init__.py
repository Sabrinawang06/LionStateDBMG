from flask import Flask, render_template, redirect, url_for, request
import sqlite3
import hashlib
from change_pass import change_password
from login_validate import validate
from create_assignment import create_assignment


app = Flask(__name__, template_folder='templates')


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        identity = request.form['identity']
        completion = validate(username, password, identity)
        if completion==False:
            error = 'Invalid Credentials. Please try again.'
        elif username=="administrator@lionstate.edu":
            return redirect(url_for('ad', username=username, identity='Administrator'))
        elif identity=="Student":
            return redirect(url_for('welcome', username=username, identity=identity))
        elif identity=="Professor":
            return redirect(url_for('welcome_prof', username=username, identity=identity))

    return render_template('login.html', error=error)



@app.route('/student<identity>/<username>',methods=['GET', 'POST'])
def welcome(username, identity):
    connection = sqlite3.connect("database.db")
    # course information
    cursor=connection.execute("select course_id, section_no from Enrolls WHERE student_email=?;", (username,))
    course_data=cursor.fetchall()



    connection.execute("""
                DROP TABLE IF EXISTS table1;""")


    connection.execute("""
            CREATE TABLE table1 AS
            select H.course_id, H.sec_no, round((sum(H.grade)*0.5+sum(E.grades)*0.5),0) AS [Class Grade]
            FROM Homework_grades H, Exam_grades E
            WHERE E.student_email=H.student_email and H.course_id=E.course_id and H.sec_no=E.sec_no and E.student_email=?
            GROUP BY H.course_id, H.sec_no;
            
            """, (username,))


    connection.executescript("""
            ALTER TABLE table1
            add letter TEXT;
            DROP TABLE if exists letter;
            DROP TABLE IF EXISTS table2;
            
            CREATE TABLE letter (alpha text);
            INSERT INTO letter(alpha) values ('A');
            INSERT INTO letter(alpha) values ('B');
            INSERT INTO letter(alpha) values ('C');
            
            
            
            CREATE TABLE table2 AS
            SELECT table1.course_id AS Course, table1.sec_no AS Section, table1.[Class Grade],letter.alpha
            FROM letter, table1
            WHERE (table1.[Class Grade]>90 AND letter.alpha=='A') or (table1.[Class Grade]>70 AND table1.[Class Grade]<89 AND letter.alpha=='B')
            or (table1.[Class Grade]<=70 AND letter.alpha=='C');""")
            
            
            
    letter_grade = connection.execute("""select * from table2; """)

    letter=letter_grade.fetchall()

    #home work grade
    homework=connection.execute('select course_id, sec_no, hw_no, grade FROM Homework_grades where student_email=?;', (username,))
    homework_data=homework.fetchall()

    # Exam grade
    exam = connection.execute('select course_id, sec_no, exam_no, grades FROM Exam_grades where student_email=?;',
                                  (username,))
    exam_data = exam.fetchall()

    #personal information
    info=connection.execute('select s.email,s.name,s.age,s.major, s.street, s.zipcode,z.city,z.state from student s,zipcode z where email=? AND s.zipcode=z.zipcode;', (username,))
    info_data=info.fetchall()

    prof_info=connection.execute("""
    select DISTINCT P.name, P.email, P.office_address, P.department
    FROM Sections S, Professor p,Prof_team_members T, Enrolls E
    WHERE T.team_id=P.email AND E.course_id=S.course_id AND S.prof_team_id=T.prof_email AND E.student_email=?;
    """, (username,))

    prof_data=prof_info.fetchall()



    class_average=connection.execute("""
    select course_id, sec_no, hw_no,min(grade),round(avg(grade),1),max(grade)
    FROM Homework_grades
    where course_id in (select E.course_id FROM Enrolls E WHERE E.student_email=?)
    AND sec_no in (select E.section_no FROM Enrolls E WHERE E.student_email=?)
    group by course_id, sec_no,hw_no;""", (username, username))


    hw_average=class_average.fetchall()

    exam_average = connection.execute("""
       select course_id, sec_no, exam_no,min(grades),round(avg(grades),1),max(grades)
       FROM Exam_grades
       where course_id in (select E.course_id FROM Enrolls E WHERE E.student_email=?)
       AND sec_no in (select E.section_no FROM Enrolls E WHERE E.student_email=?)
       group by course_id, sec_no,exam_no;""", (username, username))

    exam_data=exam_average.fetchall()



    capstone=connection.execute("""select A.student_email,A.team_id,A.course_id,A.sec_no,B.sponsor_id
from Capstone_Team_Members A ,Capstone_section B
where  A.course_id=B.course_id AND A.sec_no=B.sec_no AND
  A.team_id = (select Capstone_Team_Members.team_id from Capstone_Team_Members where Capstone_Team_Members.student_email=?) AND
   A.course_id = (select Capstone_Team_Members.course_id from Capstone_Team_Members where Capstone_Team_Members.student_email=?)AND
    A.sec_no =(select Capstone_Team_Members.sec_no from Capstone_Team_Members where Capstone_Team_Members.student_email=?);

""", (username,username,username))

    capstone_info=capstone.fetchall()

    for row in info_data:
        for a in range(8):
            if row[a] == None:
                print(row[7])
                row=list(row)
                row[a]="(Missing Information)"
                print(row[7])
        email=row[0]
        name=row[1]
        age=row[2]
        major=row[3]
        street=row[4]
        zipcode=row[5]
        city=row[6]
        state=row[7]



    error = None

    if request.method=="POST":

        oldpassword = request.form['oldpassword']
        newpassword = request.form['newpassword']
        newpassword2 = request.form['newpassword2']
        complete=change_password('student',username,oldpassword,newpassword,newpassword2)

        if complete==False:
            error="Please make sure the password match up"
        else:
            error="successfully changed the password"

    connection.close()

    return render_template('welcome.html', message="Welcome\n"+username+", You logged in as "+identity,
                           value=letter,
                           value2=homework_data,
                           value3=exam_data,
                           value4=prof_data,
                           value5=hw_average,
                           value6=exam_data,
                           info1=email+'\n'+name+'\n'+age, info4=major, info5=street+city+","+state+zipcode,
                           cap=capstone_info, course=course_data,
                           error=error)



####prof###############

@app.route('/prof<identity>/<username>', methods=['GET', 'POST'])
def welcome_prof(username, identity):
    connection = sqlite3.connect("database.db")

    course_data = []

    if request.method == 'POST':
        prehomework = request.form['prehomework']
        preexam = request.form['preexam']

        cursor = connection.execute("""
                  select E.student_email,E.course_id,E.section_no,HG.hw_no, HG.grade, EG.exam_no,EG.grades
                  from Enrolls E, Sections S, Homework_grades HG, Exam_grades EG
                  where E.course_id=S.course_id AND
                S.course_id=HG.course_id AND
                S.course_id=EG.course_id AND
                E.section_no=S.sec_no AND
                S.sec_no=HG.sec_no AND
                S.sec_no=EG.sec_no AND
                E.student_email=HG.student_email AND
                E.student_email=EG.student_email AND
                HG.hw_no=? AND EG.exam_no=?
                AND S.prof_team_id in
                (select P.prof_email from Prof_team_members P where P.team_id =?);""", (prehomework, preexam, username))

        course_data = cursor.fetchall()

        return render_template('welcome_prof.html', message="Welcome\n" + username + ", You logged in as " + identity,
                               value=course_data)



    capstone=connection.execute("""
    Select course_id, sec_no FROM Capstone_section WHERE sponsor_id in 
    (select prof_email from Prof_team_members where team_id=?);""", (username,))

    capstone_info=capstone.fetchall()

    return render_template('welcome_prof.html',
                           message="Welcome\n"+username+", You logged in as "+identity,
                           value=course_data,
                           value2=capstone_info)





###create new assignment
@app.route('/create',methods=['GET', 'POST'])
def create():
    connection = sqlite3.connect("database.db")
    if request.method=="POST":
        course = request.form['course']
        section =request.form['section']
        assignment_type=request.form['assignment']
        number=request.form['number']
        details=request.form['comments']

        if assignment_type == 'Homework':
            connection.execute("INSERT INTO Homework (course_id, sec_no, hw_no, hw_details) values (?,?,?,?);",
                               (course, section, number, details))
            connection.execute(""" INSERT INTO Homework_grades (student_email,course_id, sec_no, hw_no, grade)
                                    SELECT student_email,?,?,?, null
                                    FROM Homework_grades H
                                    WHERE H.course_id=? AND H.sec_no=?;""", (course, section, number, course, section))

            connection.commit()

        if assignment_type == 'Exam':
            connection.execute("INSERT INTO Exams (course_id, sec_no, exam_no, exam_details) values (?,?,?,?);",
                               (course, section, number, details))
            connection.execute(""" INSERT INTO Exam_grades (student_email,course_id, sec_no, exam_no, grades)
                                                SELECT student_email,?,?,?, null
                                                FROM Exam_grades H
                                                WHERE H.course_id=? AND H.sec_no=?;""",
                               (course, section, number, course, section))

            connection.commit()

    return render_template('welcome_prof.html', message='Welcome Back')



@app.route('/change',methods=['GET', 'POST'])
def change_grade():
    ##change grade



    if request.method == 'POST':

        try:

            email=request.form['email[]']
            print('you finished email')

            course_no = request.form['course_no[]']
            section_no = request.form['section_no[]']
            hw = request.form['hw[]']
            print('you finished hw')
            hw_grade = request.form['hwgrade[]']
            print('you finished hw_grade')

            exam = request.form['exam[]']
            print('you finished exam')
            exam_grade = request.form['examgrade[]']
            print('you are at the end')


            print(email)

            with sqlite3.connect("database.db") as connection:
                cur = connection.cursor()
                cur.execute("""UPDATE Homework_grades
                               SET grade=?
                               WHERE student_email=? AND course_id=? AND sec_no=? AND hw_no=?;""",
                                   (hw_grade, email, course_no, section_no, hw))
                cur.execute("""UPDATE Exam_grades
                               SET grades=?
                               WHERE student_email=? AND course_id=? AND sec_no=? AND exam_no=?;""",
                                   (exam_grade, email, course_no, section_no, exam))

                connection.commit()
                message = "Record successfully added"
                print(email)

        except:
            connection.rollback()
            message = "error in insert operation"

        finally:
            return render_template('welcome_prof.html', message="welcome back")
            connection.close()



#################ADMIN ###############

@app.route('/administrator',methods=['GET', 'POST'])
def ad():
    return render_template('ad.html', message="Welcome")

@app.route('/enroll',methods=['GET', 'POST'])
def enroll():
    message = "Not Complete"
    connection = sqlite3.connect("database.db")
    if request.method=="POST":
        semail=request.form['student_mail']
        course=request.form['course']
        section=request.form['section']
        connection.execute("""INSERT INTO Enrolls (student_email, course_id, section_no)
                                values (?,?,?);""",(semail,course,section))
        connection.commit()
        message='Enroll Successfully'
        connection.close()

    return render_template('ad.html', message=message)



@app.route('/assign',methods=['GET', 'POST'])
def assign_prof():
    message = "Not Complete"
    connection = sqlite3.connect("database.db")
    if request.method == "POST":
        course_id = request.form['course']
        pemail = request.form['pemail']

        connection.execute("""
        UPDATE Sections
        SET prof_team_id=(SELECT prof_email
        FROM Prof_team_members
        WHERE team_id=?)
        WHERE course_id=?;
        """, (pemail,course_id))

        connection.commit()
        message='Assignment Professor Team Successfully'

        connection.close()

    return render_template('ad.html', message=message)


@app.route('/course',methods=['GET', 'POST'])
def create_course():
    message="Not Complete"
    connection = sqlite3.connect("database.db")
    if request.method == "POST":
        course_id = request.form['course']
        course_name = request.form['course_name']
        section = request.form['section']
        section_type = request.form['type']
        section_limit = request.form['limit']
        details = request.form['details']

        connection.execute("""
        INSERT INTO Course (course_id, course_name, course_description) 
        VALUES (?,?,?);""",(course_id,course_name,details))

        if section=='1':
            connection.execute("""
            INSERT INTO Sections (course_id, sec_no, section_type, "limit", prof_team_id) 
            VALUES (?,'1.0',?,?,NULL);""", (course_id, section_type,section_limit) )

        elif section=="2":
            connection.execute("""
                        INSERT INTO Sections (course_id, sec_no, section_type, "limit", prof_team_id) 
                        VALUES (?,'1.0',?,?,NULL);""", (course_id, section_type, section_limit))
            connection.execute("""
                        INSERT INTO Sections (course_id, sec_no, section_type, "limit", prof_team_id) 
                        VALUES (?,'2.0',?,?,NULL);""", (course_id, section_type, section_limit))


        connection.commit()
        message="Add Course Successfully"

        connection.close()

    return render_template('ad.html', message=message)

@app.route('/delete',methods=['GET', 'POST'])
def delete_course():
    message="Incomplete"
    connection = sqlite3.connect("database.db")
    if request.method == "POST":
        course_id = request.form['course']
        connection.execute("""DELETE FROM Course
        WHERE course_id=?;""",(course_id,))
        connection.execute("""DELETE FROM Sections
        WHERE course_id=?;""", (course_id,))

        connection.commit()
        message = "Delete Course Successfully"

        connection.close()

    return render_template('ad.html', message=message)






@app.errorhandler(500)
def internal_error(error):

    return render_template('login.html'), 500

if __name__ == '__main__':
    app.run(debug=True)



####read data for students course information
