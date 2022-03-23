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


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/findPage", methods=['POST'])
def find():
    return render_template('GetEmp.html')

@app.route("/addPage", methods=['POST'])
def add():
    return render_template('AddEmp.html')

@app.route("/editPage", methods=['POST'])
def edit():
    getemp_id = request.form['emp_id']
    get_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(get_sql, (getemp_id))
    db_conn.commit()
    for i in cursor:
        getemp_id = i[0]
        first_name = i[1]
        last_name = i[2]
        pri_skill = i[3]
        location = i[4]

    cursor.close()

    return render_template('EditEmp.html', eid=getemp_id, fname=first_name, lname=last_name, skill=pri_skill, location=location)

@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name

    finally:
        cursor.close()

    return render_template('Home.html')

@app.route("/editemp", methods=['POST'])
def EditEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']

    update_sql = "UPDATE employee SET emp_id= %s , first_name= %s , last_name= %s , pri_skill= %s , location= %s WHERE emp_id= %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (emp_id, first_name, last_name, pri_skill, location, emp_id))
    db_conn.commit()
    cursor.close()
    return render_template('Home.html')

@app.route("/fetchdata", methods=['POST'])
def ShowEmp():
    getemp_id = request.form['emp_id']
    get_sql = "SELECT * FROM employee WHERE emp_id = %s"
    cursor = db_conn.cursor()

    cursor.execute(get_sql, (getemp_id))
    db_conn.commit()
    for i in cursor:
        getemp_id = i[0]
        first_name = i[1]
        last_name = i[2]
        pri_skill = i[3]
        location = i[4]

    cursor.close()
    return render_template('GetEmpOutput.html', id=getemp_id, fname=first_name, lname=last_name, skill=pri_skill, location=location)

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
