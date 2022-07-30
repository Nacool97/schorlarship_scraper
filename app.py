import math
from flask import Flask, render_template
from pymongo import MongoClient
app = Flask(__name__)

cleint = MongoClient('localhost',27017)
collection = cleint['nacool_projects']['scholarships']
data = list(collection.find())
page_number = 1
cont_count = 5
@app.route('/',defaults={'page':1})
@app.route('/<page>')
def index(page):
    sch = data
    from_page = (int(page)-1)*cont_count
    to_page = int(page)*cont_count
    pagination = math.ceil(len(data)/cont_count)
    return render_template('index.html',data=sch,from_page=from_page,to_page=to_page,pagination=pagination)

if __name__ == '__main__':
    app.run('0.0.0.0',port=8080)