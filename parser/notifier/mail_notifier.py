from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
import mysql.connector, os
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
app = Flask(__name__)
app.secret_key = "any@random#string"


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'nakul.scholarsmate@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get("scholars_mail")
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
            deadline = datetime.strptime(result[2],"%d/%m/%Y")
        except Exception as e:
            deadline = None
        if deadline and (deadline - today).days <= 7:
            alerts = (result[0], result[1])
        if alerts:
            alerts_list.append(alerts)
    return alerts_list

def update_alert_flag(email,scholarship_id):
    query = f"update scholars_subs set send_alert = {False} where scholarship_id = '{scholarship_id}' and email = '{email}'"
    cursor.execute(query)
    mydb.commit()
    print(cursor.rowcount, "row(s) updated")

# send alerts and update the send_alerts flag
def send_mail_and_update(data):
    all_scholarships = list(collection.find({"expired":{"$ne":True}}))
    for d in data:
        scholarship_id = d[1]
        email = d[0]
        for sch in all_scholarships:
            if str(sch.get('_id')) == scholarship_id:
                send_mail(email, sch)
                update_alert_flag(email,scholarship_id)
    return "Done"

def send_mail(email, scholarship):
    name = "User"
    message = Message(
        f"Scholarship Deadline Alert ",
        sender='nacool.scholarsmate@gmail.com',
        recipients=[email]
    )
    message.html = f'Hello {name},<br>This the deadline alert for the {scholarship["name"]}.<br>Deadline is on {scholarship["deadline"]}.<br>Here is the <a href="https://scholarsmate.uk/view/{scholarship["_id"]}">scholarship url</a>'
    mail.send(message)
    return 'Sent'
@app.route("/")
def send_notification():
    data = get_all_mails_for_alerts()
    print(data)
    result = get_all_email_id(data)
    print(result)
    return send_mail_and_update(result)

if __name__ =="__main__":
    app.run(host="0.0.0.0",port=5000)

