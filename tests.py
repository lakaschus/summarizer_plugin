import requests

url = "http://localhost:5003/summary"
data = {"url": "https://example.com/"}
response = requests.post(url, json=data)
print(response.json())
