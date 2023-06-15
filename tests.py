import requests

url = "http://localhost:5005/div"
data = {"num1": 5, "num2": 3, "digits": 4}
response = requests.post(url, json=data)
print(response.json())  # Output: {"result": 2.000}
