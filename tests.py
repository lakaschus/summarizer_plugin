import requests

url = "http://localhost:5003/summary"
data = {"url": "https://www.tagesschau.de/ausland/asien/blinken-besuch-peking-vorab-100.html"}
response = requests.post(url, json=data)
print(response.json())
