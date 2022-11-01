from pymongo import MongoClient
import re
from datetime import datetime, timedelta
import json
from difflib import SequenceMatcher
from math import ceil

client = MongoClient('localhost',27017)
collection = client['nacool_projects']['scholarships']
scholarship_lists = list(collection.find())
def check_for_duplicate_data(data):
    if not data.get('url'):
        return True
    sch = collection.find_one({
        'url':data['url']
    })
    if sch:
        return True
    for scholarship in scholarship_lists:
        print(data)
        similarity = SequenceMatcher(None,data['name'],scholarship['name']).ratio()*100
        if ceil(similarity) > 85:
            return True
    return False
def save_data(data_list):
    new_data = []
    for data in data_list:
        if check_for_duplicate_data(data):
            continue
        new_data.append(data)
    if new_data:
        collection.insert_many(new_data)
    print('saved-data-to-db')
def get_valid_date_object(date):
    date_obj = None
    try:
        date_obj = datetime.strptime(date,'%d %b %Y')
    except Exception:
        pass
    try:
        date_obj = datetime.strptime(date,'%d %B %Y')
    except Exception:
        pass
    try:
        date_obj = datetime.strptime(date,'%d %b %y')
    except Exception:
        pass
    try:
        date_obj = datetime.strptime(date,'%d %B %Y')
    except Exception:
        pass
    try:
        date_obj = datetime.strptime(date,'%d %m %Y')
    except Exception:
        pass
    return date_obj
def parse_scholarship_portal(body):
    data = json.loads(body)
    scholarship_list = []
    for d in data:
        scholarship = {}
        deadline =  get_valid_date_object(d['deadline']) if d.get('deadline') and d['deadline'] else None
        scholarship['expired'] = False
        if deadline and deadline < datetime.now():
            scholarship['expired'] = True
        number_of_days = (datetime.now() + timedelta(days=50)).timestamp()
        if deadline:
            number_of_days = int(datetime.now().timestamp() - deadline.timestamp())
        exlude_keys = ['tile','amount','deadline']
        scholarship['metadata'] = [{k: d[k] for k in set(list(d.keys()))-set(exlude_keys)}]
        scholarship['name'] = d['title'] if d.get('title') else "NA"
        scholarship['amount'] = d['amount'] if d.get('amount') and d['amount'] else "NA"
        scholarship['number_of_days_left'] = number_of_days
        if deadline:
            scholarship['deadline'] = deadline.strftime('%d/%m/%Y')
        else:
            scholarship['deadline'] = "Data Not Available"
        scholarship_list.append(scholarship)
    save_data(scholarship_list)
