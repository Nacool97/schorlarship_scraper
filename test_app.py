from datetime import datetime
from email.policy import default
from bson import ObjectId
from flask import Flask, render_template, request, session, redirect, url_for
from flask_mail import Mail, Message
import mysql.connector
from pymongo import MongoClient
import json
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
# find the non expired scholarships
data = list(collection.find({'expired': False}).sort('days_left', 1))
#data = open("/home/nakulk/pynacool/schorlarship_scraper/test_data.json")
#data = json.load(data)
page_number = 1
cont_count = 5

mydb = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="root",
    database="scholarsmate",
    auth_plugin='mysql_native_password'
)

cursor = mydb.cursor()


def get_scholars(email, scholarship_id):
    if scholarship_id:
        cursor.execute(
        f"SELECT * from scholars_subs where scholarship_id = '{scholarship_id}' and email = '{email}'")
        result = cursor.fetchall()
        print(result)
        if result:
            return result 
    cursor.execute(f"SELECT password FROM scholars where email = '{email}'")
    result = cursor.fetchone()
    if result:
        return result[0]
    return


def insert_scholars(email, password):
    sql = "INSERT INTO scholars (email, password) VALUES (%s, %s)"
    val = (email, password)
    cursor.execute(sql, val)
    mydb.commit()
    print(cursor.rowcount, "record inserted.")


def get_scholars_subs(scholarship_id):
    cursor.execute(
        f"SELECT email from scholars_subs where scholarship_id = '{scholarship_id}'")
    result = cursor.fetchall()
    if result:
        return list(*zip(*result))
    return None


def insert_scholars_subs(email, scholarship_id, deadline):
    if get_scholars(email,scholarship_id):
        print(scholarship_id)
        sql = f"update scholars_subs set send_alert = {True} where scholarship_id = '{scholarship_id}' and email = '{email}'"
        cursor.execute(sql)
        mydb.commit()
        print(cursor.rowcount, "row(s) deleted")
        return
    sql = "INSERT INTO scholars_subs (email, scholarship_id, send_alert, deadline) VALUES (%s, %s, %s, %s)"
    val = (email, scholarship_id, True, deadline)
    cursor.execute(sql, val)
    mydb.commit()
    print(cursor.rowcount, "record inserted.")


def delete_scholars_subs(email, scholarship_id):
    sql = f"update scholars_subs set send_alert = {False} where scholarship_id = '{scholarship_id}' and email = '{email}'"
    cursor.execute(sql)
    mydb.commit()
    print(cursor.rowcount, "row(s) deleted")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        try:
            name = request.form.get('email')
            password = request.form.get('password')
            db_password = get_scholars(name)
            if db_password and db_password == password:
                session['email'] = name
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Invalid credentials')
        except Exception as e:
            print(e)
            return render_template('login.html', error='An Error Occured')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        if request.method == 'GET':
            return render_template('signup.html')
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            cnf_password = request.form.get('cnf_password')
            db_password = get_scholars(email)
            if db_password:
                return render_template('signup.html', error="Email already exists")
            elif len(password) < 8 or len(password) > 15:
                return render_template('signup.html', error="Password must contain character between 8 - 15")
            elif password != cnf_password:
                return render_template('signup.html', error="Passwords do not match")
            else:
                insert_scholars(email=email, password=password)
                return render_template('login.html')
    except Exception as e:
        print(e)
        return render_template('signup.html', error="Error Occured Try Again")


@app.route('/logout')
def logout():
    session.pop('email')
    return redirect(url_for('index'))

# default page


@app.route('/', defaults={'page': 1})
@app.route('/<page>')
def index(page):
    current = int(page)
    next_page = current+1
    previous_page = current-1
    if current < 1:
        current = 1
        previous_page = None
    if current*5 >= len(data):
        current = int(len(data)/5)
        next_page = None
    from_page = (current-1)*cont_count
    to_page = current*cont_count
    # get the last 5 entires i.e. recent 5 scraped enterirs which are not expired
    recent_data = list(collection.find(
        {'expired': False}).sort('_id', -1).limit(5))
    #recent_data = data
    if session.get('email'):
        return render_template('logged_index.html', data=data, from_page=from_page, to_page=to_page, current=current, next=next_page, previous=previous_page, recent_data=recent_data, session=session)
    return render_template('index.html', data=data, from_page=from_page, to_page=to_page, current=current, next=next_page, previous=previous_page, recent_data=recent_data, session=session)


@app.route('/view', defaults={'/view/<index>': "630e275b1b232898cd94af20"})
@app.route('/view/<string:index>')
def scholarship_page(index):
    scholarship_data = collection.find_one({'_id': ObjectId(index)})
    #scholarship_data = data
    # get the last 5 entires i.e. recent 5 scraped enterirs which are not expired
    recent_data = list(collection.find(
        {'expired': False}).sort('_id', -1).limit(5))
    #recent_data = data
    return render_template('blog-single.html', data=scholarship_data, recent_data=recent_data)


@app.route("/mail")
def send_mail():
    sch_id = request.args.get('sch_id')
    recipient = request.args.get('recipient')
    name = "User"
    if session.get('email'):
        name = session.get('email')
    scholarship = collection.find_one({'_id': sch_id})
    scholarship = data[1]
    message = Message(
        f"Scholarship Deadline Alert ",
        sender='scholarsmate@gmail.com',
        recipients=[recipient]
    )
    message.body = f'Hello {name}\n This the deadline alert for the {scholarship["name"]}.\nDeadline is on {scholarship["deadline"]}.\nHere is the <a href="https://scholarlsmate.uk/view/{scholarship["_id"]}">scholarship url</a>'
    mail.send(message)
    return redirect(url_for('index'))


@app.route('/alert_me', methods=['GET', 'POST'])
def alert_me():
    data = request.json
    sch_id = data.get('sch_id')
    deadline = data.get('deadline')
    insert_scholars_subs(session['email'], sch_id, deadline)
    return redirect(url_for('index'))


@app.route('/unalert_me', methods=['GET', 'POST'])
def unalert_me():
    data = request.json
    sch_id = data.get('sch_id')
    deadline = data.get('deadline')
    db_email = get_scholars_subs(sch_id)
    if not db_email or session['email'] in db_email:
        delete_scholars_subs(session['email'], sch_id)
    return redirect(url_for('index'))


def send_email(sch_id, recipient):
    #sch_id = request.args.get('sch_id')
    #recipient = request.args.get('recipient')
    name = "User"
    if session.get('email'):
        name = session.get('email')
    scholarship = collection.find_one({'_id': sch_id})
    #scholarship = data[1]
    message = Message(
        f"Scholarship Deadline Alert ",
        sender='nacool.scholarsmate@gmail.com',
        recipients=[recipient]
    )
    message.html = f'Hello {name},<br>This the deadline alert for the {scholarship["name"]}.<br>Deadline is on {scholarship["deadline"]}.<br>Here is the <a href="https://scholarlsmate.uk/view/{scholarship["_id"]}">scholarship url</a>'
    mail.send(message)
    return 'Sent'


if __name__ == '__main__':
    app.run('0.0.0.0', port=5080, threaded=True)
