import os,requests
print(os.environ["scholars_mail"])
response = requests.get("http://192.168.1.13:5000")
print(f"Status: {response.status_code}\n Response: {response.content}")