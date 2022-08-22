import re
import requests
import json
from datetime import datetime
import pika
from bs4 import BeautifulSoup
from pymongo import MongoClient

client = MongoClient('localhost',port=27017)
collection = client['nacool_projects']['scholarships']

scholarships = open('/home/nacool/Desktop/Projects/scholarship_scraper/scholarship_url.json')
urls = json.load(scholarships)
sch_data = urls[0]
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def send_message(queue_name,payload):
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',routing_key=queue_name,body=payload)
    connection.close()

# check if scholarship is expired and update exipred field
def check_if_expired(scholarship):
    if datetime.strptime(scholarship['deadline'],'%d/%m/%Y') < datetime.now():
        collection.update_one({'_id':scholarship['_id']},
            {'$set':{'expired':True}})
        return True 
    return False

# check if scholarship is already fecthed
def check_for_duplicate(url):
    scholarship = collection.find_one({
        'url':url
    })
    if scholarship:
        check_if_expired(scholarship)
        return True
    return False
    

def parser_webpage(content):
    scholarship_list = []
    web_data = content.find_all('div',attrs={'class':'post clearfix'})
    if not web_data:
        return {}
    for data in web_data:
        scholarship = {}
        scholarship['expired'] = False
        scholarship['schship_name'] = data.find('h2').text.strip()
        scholarship['schship_url'] = data.find('a').get('href')
        isfetched = check_for_duplicate(scholarship['schship_url'])
        if isfetched:
            last_update = datetime.now()
            date = last_update.strftime('%d/%m/%Y')
            collection.update_one({'url':scholarship['schship_url']},
            {
                '$set':{'last_update':date}
            })
            continue
        data_list = data.find_all('div',attrs={'class':'post_column_1'})
        if len(data_list) != 2:
            continue
        scholarship['schship_for'] = data_list[0].text.strip()
        deadline = data_list[1].text.strip()
        m = re.search(r'(\d+\s*[a-z]+\s*\d{4})',deadline, re.I) 
        if m:
            deadline = m.group(1)
            try:
                try:
                    date_str = datetime.strptime(deadline,'%d %b %Y').isoformat()
                except Exception as e:
                    date_str = datetime.strptime(deadline,'%d %B %Y').isoformat()
                date_obj = datetime.strptime(date_str,"%Y-%m-%dT%H:%M:%S")
                if date_obj < datetime.now():
                    scholarship['expired'] = True
                deadline = date_obj.strftime('%d/%m/%Y')
            except Exception:
                continue
        scholarship['schship_deadline'] = deadline
        
        last_update = datetime.now()
        date = last_update.strftime('%d/%m/%Y')
        scholarship['schship_last_updated'] = date
        if scholarship:
            scholarship_list.append(scholarship)
    return scholarship_list

def fetch_data():
    response = None
    try:
        response = requests.get(sch_data['url'],timeout=100)
        response.raise_for_status
    except Exception as e:
        print(e)
        return []
    if not response:
        print('No Data found')
        return []
    results = []
    soup = BeautifulSoup(response.content,'lxml')
    results = parser_webpage(soup)
    pagination = soup.find('div',attrs={'class':'wp-pagenavi'})
    pagination_links = pagination.find_all('a')
    if pagination_links:
        for url in pagination_links:
            try:
                response = requests.get(url.get('href'),timeout=100)
                response.raise_for_status
            except Exception as e:
                continue
            soup = BeautifulSoup(response.content,'lxml')
            results.extend(parser_webpage(soup))
    return results

def main():
    scholarships = fetch_data()
    if scholarships:
        send_message(queue_name='new_data_scholars4dev',payload=json.dumps(scholarships))
        print('Message queued')
if __name__ == '__main__':
    main()    