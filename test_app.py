from datetime import datetime
from flask import Flask, render_template
from pymongo import MongoClient
app = Flask(__name__)
# get the mongodb access
cleint = MongoClient('localhost',27017)
collection = cleint['nacool_projects']['test_scholarships']
# find the non expired scholarships
data = list(collection.find({'expired':False}).sort('days_left'))
page_number = 1
cont_count = 5

#default page
@app.route('/',defaults={'page':1})
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
    recent_data = list(collection.find({'expired':False}).sort('_id',-1).limit(5))
    
    return render_template('index.html',data=data,from_page=from_page,to_page=to_page,current=current,next=next_page,previous=previous_page,recent_data=recent_data)
@app.route('/id:<id>')
def scholarship_page(id):
    return id
if __name__ == '__main__':
    app.run('0.0.0.0',port=5080)