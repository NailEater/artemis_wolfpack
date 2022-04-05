from flask import Flask, render_template, request, g, redirect, session, url_for
from pymysql import connections
import sys
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)

output = {}
table = 'employee'
    
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

query = "SELECT emp_id, emp_username, emp_password from employee"
cursor = db_conn.cursor()

cursor.execute(query)
records = cursor.fetchall()

users = []

for row in records:
    users.append(User(id=row[0], username=row[1], password=row[2]))


app.secret_key = 'somesecretkeythatonlyishouldknow'

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user
        

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['username']
        password = request.form['password']
        user = 0
        
        for x in users:
            try:
                if x.username == username:
                    user = [x][0]
            except:
                error = 'Invalid username or password. Please try again!'
                return render_template('login-page.html', error = error)

        if user and user.password == password:
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('profile'))

        if user and user.password != password:
            error = 'Invalid username or password. Please try again!'
            return render_template('login-page.html', error = error)

        error = 'Invalid username or password. Please try again!'
        return render_template('login-page.html', error = error)

    return render_template('login-page.html')

@app.route('/home')
def profile():
    if not g.user:
        return redirect(url_for('login'))

    return render_template('Home.html',user=session['username'])

@app.route('/dropsession')
def dropsession():
    session.pop('username', None)
    session.pop('user_id', None)
    g.user = None
    return redirect('/')

@app.route("/findPage", methods=['POST'])
def find():
    return render_template('GetEmp.html')

@app.route("/addPage", methods=['POST'])
def add():
    return render_template('AddEmp.html')

@app.route("/editPage", methods=['POST'])
def edit():
    emp_id = request.form['emp_id']
    get_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(get_sql, (emp_id))
    db_conn.commit()
    for i in cursor:
        emp_id = i[0]
        emp_username = i[1]
        emp_name = i[2]
        gender = i[3]
        contact_num = i[4]
        emp_email = i[5]
        emp_password = i[6]

    cursor.close()

    return render_template('EditEmp.html', emp_id=emp_id, emp_username=emp_username, emp_name=emp_name, gender=gender, contact_num=contact_num, emp_email=emp_email, emp_password=emp_password)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    emp_username = request.form['emp_username']
    emp_name = request.form['emp_name']
    gender = request.form['gender']
    contact_num = request.form['contact_num']
    emp_email = request.form['emp_email']
    emp_password = request.form['emp_password']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (emp_id, emp_username, emp_name, gender, contact_num, emp_email, emp_password))
        db_conn.commit()
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')
        s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
        bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
        s3_location = (bucket_location['LocationConstraint'])
        
        if s3_location is None:
                s3_location = ''
        else:
                s3_location = '-' + s3_location

        object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

    finally:
        cursor.close()

    return render_template('Home.html')

@app.route("/editemp", methods=['POST'])
def EditEmp():
    emp_id = request.form['emp_id']
    emp_username = request.form['emp_username']
    emp_name = request.form['emp_name']
    gender = request.form['gender']
    contact_num = request.form['contact_num']
    emp_email = request.form['emp_email']
    emp_password = request.form['emp_password']

    update_sql = "UPDATE employee SET emp_id= %s , emp_username= %s , emp_name= %s , gender= %s , contact_num= %s , emp_email= %s, emp_password= %s WHERE emp_id= %s"   
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (emp_id, emp_username, emp_name, gender, contact_num, emp_email, emp_password, emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('Home.html')

@app.route("/fetchdata", methods=['POST'])
def ShowEmp():
    emp_id = request.form['emp_id']
    get_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(get_sql, (emp_id))
    db_conn.commit()
    for i in cursor:
        emp_id = i[0]
        emp_username = i[1]
        emp_name = i[2]
        gender = i[3]
        contact_num = i[4]
        emp_email = i[5]

    cursor.close()
    return render_template('GetEmpOutput.html', emp_id=emp_id, emp_username=emp_username, emp_name=emp_name, gender=gender, contact_num=contact_num, emp_email=emp_email)

@app.route("/delete", methods=['POST'])
def DelEmp():
    emp_id = request.form['emp_id']

    del_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(del_sql, (emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('Home.html')

@app.route("/attendHome", methods=['GET', 'POST'])
def atthome():
    return render_template('attendanceHome.html')

@app.route("/addAttendanceData", methods=['POST'])
def attadd():
    return render_template('attendance.html')

@app.route("/searchAttendanceData", methods=['POST'])
def searchAttendanceData():                         
    return render_template('GetAttEmp.html')

@app.route("/addAttend", methods=['POST'])
def addAttend():
    attendance_ID = request.form['attendance_ID']  
    emp_ID = request.form['emp_ID']
    attendance_date = request.form['attendance_date']
    attendance_status = request.form['attendance_status']
    
    

    insert_sql = "INSERT INTO attendance (attendance_ID, emp_ID, attendance_date, attendance_status) VALUES (%s, %s, %s, %s)"
    cursor = db_conn.cursor()


    try:

        cursor.execute(insert_sql, (attendance_ID, emp_ID, attendance_date, attendance_status))
        db_conn.commit()
        
    finally:
        cursor.close()

    print("all modification done...")
    return render_template('GetAttEmp.html')
    
  
@app.route("/fetchattdata",methods=['POST'])
def fetchattdata():
    cursor = db_conn.cursor()
    cursor.execute("SELECT attendance_ID, emp_ID, attendance_date, attendance_status FROM attendance")
    i = cursor.fetchall()
    return render_template('GetAllAttendance.html', data=i) 


@app.route("/showData", methods=['POST'])
def showData():

    attendance_ID = request.form['attendance_ID']
    select_employee_query = "SELECT attendance_ID, emp_ID, attendance_date, attendance_status FROM attendance WHERE attendance_ID = %s"
    cursor = db_conn.cursor()
    
    cursor.execute(select_employee_query,(attendance_ID))
    db_conn.commit()
    
    for i in cursor:
       attendance_ID = i[0]
       emp_ID = i[1]
       attendance_date = i[2]
       attendance_status = i[3]
       
    cursor.close()   
    return render_template('GetAttEmpOutput.html', attendance_ID=attendance_ID, emp_ID=emp_ID, attendance_date=attendance_date, attendance_status=attendance_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
