"""
Fetcher to fetch and do minimal parsing from scholars4dev website
"""
import re
import requests
import json
from datetime import datetime,timedelta
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


# check if scholarship is expired and update exipred field
def check_if_expired(scholarship):
    '''
    check if the scholarship is expired by checking if we have passed deadline
    param: scholarship (dict)
    it if fetched from either db for newly fetched
    sets expired flag true if deadline is passed
    or
    updates number of days left
    return: None
    '''
    try:
        if datetime.strptime(scholarship['deadline'],'%d/%m/%Y') < datetime.now():
            collection.update_one({'_id':scholarship['_id']},
            {'$set':{'expired':True}})
        else:
            days_left = int(datetime.strptime(scholarship['deadline'],'%d/%m/%Y').timestamp() - datetime.now().timestamp())
            collection.update_one({'_id':scholarship['_id']},
            {'$set':{'days_left':days_left}})
    except Exception as e:
        days_left = int((datetime.now()+timedelta(days=50)).timestamp())
        collection.update_one({'_id':scholarship['_id']},
            {'$set':{'days_left':days_left}})

# check if scholarship is already fecthed
def check_for_duplicate(url):
    '''
    checks if the url is already present in the db
    param :url
    returns bool 
    True if exists
    False if doesn't exists
    '''
    scholarship = collection.find_one({
        'url':url
    })
    if scholarship:
        check_if_expired(scholarship)
        return True
    return False
    
# scrape the important data and return dict
def parser_webpage(content):
    '''
    scrapes data from the content parameter using bs4 lxml parser
    and extract follwing details
    name
    url
    deadline
    param content 
    response body from requests
    returns dict
    '''
    scholarship_list = []
    web_data = content.find_all('div',attrs={'class':'post clearfix'})
    if not web_data:
        return {}
    for data in web_data:
        scholarship = {}
        scholarship['expired'] = False
        scholarship['schship_name'] = data.find('h2').text.strip()
        scholarship['schship_url'] = data.find('a').get('href')
        #check for duplicate
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
        scholarship['country'] = "Not Sure"
        match = re.search(r'(country\:|study in\:)(.*)',deadline,re.I)
        if match:
            scholarship['country'] = match.group(2)
        m = re.search(r'(\d+\s*[a-z]+\s*\d{4})',deadline, re.I) 
        number_of_days = (datetime.now() + timedelta(days=50)).timestamp()
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
                number_of_days = int(date_obj.timestamp() - datetime.now().timestamp())
                deadline = date_obj.strftime('%d/%m/%Y')
            except Exception as e:
                print(e)
                continue
        scholarship['schship_deadline'] = deadline
        scholarship['number_of_days_left'] = number_of_days
        last_update = datetime.now()
        date = last_update.strftime('%d/%m/%Y')
        scholarship['schship_last_updated'] = date
        if scholarship:
            scholarship_list.append(scholarship)
    return scholarship_list
# fetch data from url using requests
def fetch_data():
    '''
    fetch data from the url in json file parse data
    param None
    returns list of scholarship 
    '''
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
    if not soup:
        return []
    # parse data
    results = parser_webpage(soup)
    pagination = soup.find('div',attrs={'class':'wp-pagenavi'})
    if not pagination:
        return []
    # extract all details from the next pages
    pagination_links = pagination.find_all('a')
    if pagination_links:
        # crawl every page and parse data
        for url in pagination_links:
            try:
                response = requests.get(url.get('href'),timeout=100)
                response.raise_for_status
            except Exception as e:
                continue
            soup = BeautifulSoup(response.content,'lxml')
            if not soup:
                return []
            results.extend(parser_webpage(soup))
    return results


# publish data to queue
def send_message(queue_name,payload):
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',routing_key=queue_name,body=payload)
    connection.close()

def main():
    scholarships = fetch_data()
    if scholarships:
        send_message(queue_name='new_data_scholars4dev',payload=json.dumps(scholarships))
        print('Message queued')
if __name__ == '__main__':
    main()    