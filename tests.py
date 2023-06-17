import requests

url = "http://localhost:5007/summary"
data = {"url": "https://arxiv.org/pdf/2303.10130.pdf"}
response = requests.post(url, json=data)
print(response.json())
