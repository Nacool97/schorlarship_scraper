from pymongo import MongoClient
import re
from datetime import datetime, timedelta
import json
client = MongoClient('localhost', 27017)
collection = client['nacool_projects']['scholarships']
scholarship_lists = list(collection.find())

def update_all(scholarship):
    try:
        if datetime.strptime(scholarship['deadline'],'%d/%m/%Y') < datetime.now():
            collection.update_one({'_id':scholarship['_id']},
            {'$set':{'expired':True}})
    except Exception:
        days_left = int((datetime.now()+timedelta.days(50)).timestamp())
        collection.update_one({'_id':scholarship['_id']},
            {'$set':{'days_left':days_left}})
    print(f"{scholarship['url']} --> changed")

if __name__ == "__main__":
    for sch in scholarship_lists:
        update_all(sch)