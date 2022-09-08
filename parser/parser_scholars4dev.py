'''
get data from queue and parse data form
'''
import requests
from pymongo import MongoClient
import re
from bs4 import BeautifulSoup
import json

client = MongoClient('localhost',27017)
collection = client['nacool_projects']['scholarships']

def parse_scholars4dev(body):
    data = json.loads(body)
    scholarship_list = []
    for d in data:
        scholarship = {}
        try:
            scholarship['name'] = d['schship_name'].replace('\n','').replace('\r','')
            scholarship['scholarship_for'] = d['schship_for'].replace('\n','').replace('\r','')
            scholarship['deadline'] = d['schship_deadline'].replace('\n','').replace('\r','')
            scholarship['last_update'] = d['schship_last_updated'].replace('\n','').replace('\r','')
            scholarship['days_left'] = d['number_of_days_left']
            scholarship['expired'] = d['expired']
            scholarship['country'] = d['country']
            scholarship['url'] = d['schship_url']
        except Exception as e:
            print(e)
            continue
        try:
            response = requests.get(d['schship_url'],timeout=100)
            response.raise_for_status
        except Exception as e:
            print(e)
            continue
        soup = BeautifulSoup(response.content,'lxml')
        if not soup:
            continue
        metadata = []
        metadata_content = soup.find('div',attrs={'class','entry clearfix'})
        if not metadata_content:
            continue
        titles = metadata_content.find_all('p',attrs={'style':'color: #003366;'})
        
        if not titles:
            continue
        for title in titles:
            key = title.text.lower()
            key = re.sub(r'[\:\-\(\)\@\#\!\.\'\"]+','',key,flags=re.I)
            key = key.replace(' ','-').strip()
            p_tag = title.findNext('p')
            value = title.findNext('p').text.replace("\xa0",'').strip()
            if re.search(r'Eligibility',key,re.I):
                value += ' '+title.findNext('ul').text.strip()
            if p_tag.find('a'):
                value = p_tag.find('a')['href'] 
            metadata.append({key:value})
        scholarship['metadata'] = metadata
        scholarship_list.append(scholarship)
    collection.insert_many(scholarship_list)
    print('inserted-to-db')
    return 'db-updated'
