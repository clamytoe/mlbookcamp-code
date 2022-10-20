import requests

data = '{"seniority": 3, "home": "owner", "time": 36, "age": 26, "marital": "single", "records": "no", "job": "freelance", "expenses": 35, "income": 0.0, "assets": 60000.0, "debt": 3000.0, "amount": 800, "price": 1000}'

response = requests.post(
    "http://54.162.32.9:3000/classify",
    headers={"content-type": "application/json"},
    data=data,
).text

print(response)
