from flask import Flask, render_template, request
from pymysql import connections
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

@app.route("/", methods = ['POST'])
def checklogin():
    UN = request.form['username']
    PW = request.form['password']

    #sqlconnection = sqlite3.Connection(currentlocation + "\Login.db")
    cursor = db_conn.cursor()
    query1 = "SELECT user_id, password from employee where user_id = {un} AND password = {pw}".format(un=UN, pw = PW)
    query2 = "failed"
    
    rows = cursor.execute(query1)
    #rows = rows.fetchall()
    
    test = 1
    
    #if len(rows) == 1:
    if test == 1:
        return render_template("Home.html", first_name=query1)
    else:
        return "Wrong User ID or Wrong password"

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
        emp_password = i[6]

    cursor.close()
    return render_template('GetEmpOutput.html', emp_id=emp_id, emp_username=emp_username, emp_name=emp_name, gender=gender, contact_num=contact_num, emp_email=emp_email, emp_password=emp_password)

@app.route("/delete", methods=['POST'])
def DelEmp():
    emp_id = request.form['emp_id']

    del_sql = "DELETE FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()
    cursor.execute(del_sql, (emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('Home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
