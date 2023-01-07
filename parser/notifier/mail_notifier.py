from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
import mysql.connector
from pymongo import MongoClient

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