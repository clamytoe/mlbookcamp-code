import requests

data = '[[6.4,3.5,4.5,1.2]]'

response = requests.post(
    # "http://54.162.32.9:3000/classify",
    "http://localhost:3000/classify",
    headers={"content-type": "application/json"},
    data=data,
).text

print(response)
