import requests
from bs4 import BeautifulSoup
import json
def parse_scholars4dev(body):
    data = json.loads(body)
    scholarship_list = []
    for d in data:
        scholarship = {}
        scholarship['name'] = d['schship_name'].replace('\n','').replace('\r','')
        scholarship['scholarship_for'] = d['schship_for'].replace('\n','').replace('\r','')
        scholarship['deadline'] = d['schship_deadline'].replace('\n','').replace('\r','')
        scholarship['last_update'] = d['schship_last_update'].replace('\n','').replace('\r','')
        try:
            response = requests.get(d['schship_url'])
            response.raise_for_status
        except Exception as e:
            print(e)
            continue
        