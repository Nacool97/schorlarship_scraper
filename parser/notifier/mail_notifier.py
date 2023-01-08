from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
import mysql.connector
from pymongo import MongoClient
from datetime import datetime
app = Flask(__name__)
app.secret_key = "any@random#string"

# mail_pass = "rnqgwjoocplmwnht"
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
#app.config['MAIL_USERNAME'] = 'nacool.scholarsmate@gmail.com'
#app.config['MAIL_PASSWORD'] = 'rnqgwjoocplmwnht'
app.config['MAIL_USERNAME'] = 'nakul.scholarsmate@gmail.com'
app.config['MAIL_PASSWORD'] = 'gmtptvrslfatdmbf'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

# get the mongodb access
cleint = MongoClient('localhost', 27017)
collection = cleint['nacool_projects']['scholarships']

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="scholarsmate",
    auth_plugin='mysql_native_password'
)

cursor = mydb.cursor()
# fetch all the email id scholarship_id and deadline who as sent_alert flag as 1
def get_all_mails_for_alerts():
    query = "SELECT email, scholarship_id, deadline from scholars_subs where send_alert=1"
    cursor.execute(query)
    result = cursor.fetchall()
    return result
# fetch all email and scholarship_id for deadline less than 1 week
def get_all_email_id(results):
    alerts_list = []
    today = datetime.now()
    for result in results:
        alerts =()
        try:
            deadline = datetime.strptime(result[1],"%d/%m/%YYYY")
        except Exception as e:
            deadline = None
        if deadline and deadline - today:
            pass

