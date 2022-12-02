import requests

# url = "http://localhost:9696/predict"
# url = "http://localhost:8080/predict"
url = "http://a1719971a477744278268caa197051f2-249405805.us-east-1.elb.amazonaws.com/predict"

data = {"url": "http://bit.ly/mlbookcamp-pants"}

result = requests.post(url, json=data).json()
print(result)
