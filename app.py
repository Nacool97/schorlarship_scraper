from datetime import datetime
from flask import Flask, render_template
from pymongo import MongoClient
app = Flask(__name__)

cleint = MongoClient('localhost',27017)
collection = cleint['nacool_projects']['scholarships']
data = list(collection.find({'expired':False}))
page_number = 1
cont_count = 5
@app.route('/',defaults={'page':1})
@app.route('/<page>')
def index(page):
    current = int(page)
    if current < 1:
        current = 1
    if current*5 > len(data):
        current = int(len(data)/5)
    from_page = (current-1)*cont_count
    to_page = current*cont_count
    

    return render_template('index.html',data=data,from_page=from_page,to_page=to_page,current=current)

if __name__ == '__main__':
    app.run('0.0.0.0',port=8080)