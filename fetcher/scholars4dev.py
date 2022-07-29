from datetime import datetime
from textwrap import indent
import requests
import json

import pika
from bs4 import BeautifulSoup

scholarships = open('/home/nacool/Desktop/Projects/scholarship scraper/scholarship_url.json')
urls = json.load(scholarships)
sch_data = urls[0]
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

def send_message(queue_name,payload):
    channel.queue_declare(queue=queue_name)
    channel.basic_publish(exchange='',routing_key=queue_name,body=payload)
    connection.close()

def parser_webpage(content):
    scholarship_list = []
    web_data = content.find_all('div',attrs={'class':'post clearfix'})
    if not web_data:
        return {}
    for data in web_data:
        scholarship = {}
        scholarship['schship_name'] = data.find('h2').text.strip()
        scholarship['schship_url'] = data.find('a').get('href')
        data_list = data.find_all('div',attrs={'class':'post_column_1'})
        if len(data_list) != 2:
            continue
        scholarship['schship_for'] = data_list[0].text.strip()
        scholarship['schship_deadline'] = data_list[1].text.strip()
        if not data.find('div',attrs={'class':'left'}):
            continue 
        scholarship['schship_last_updated'] = data.find('div',attrs={'class':'left'}).text
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