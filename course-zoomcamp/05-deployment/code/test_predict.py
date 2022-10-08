#!/usr/bin/env python
# coding: utf-8

import requests

# host = 'localhost'
# port = ':9696'
host = 'churn-service-env.eba-3xmswp3v.us-east-1.elasticbeanstalk.com'
port = ''
url = f'http://{host}{port}/predict'

customer_id = 'xyz-123'
customer = {
    "gender": "female",
    "seniorcitizen": 0,
    "partner": "yes",
    "dependents": "no",
    "phoneservice": "no",
    "multiplelines": "no_phone_service",
    "internetservice": "dsl",
    "onlinesecurity": "no",
    "onlinebackup": "yes",
    "deviceprotection": "no",
    "techsupport": "no",
    "streamingtv": "no",
    "streamingmovies": "no",
    "contract": "month-to-month",
    "paperlessbilling": "yes",
    "paymentmethod": "electronic_check",
    "tenure": 24,
    "monthlycharges": 29.85,
    "totalcharges": (24 * 29.85)
}


def predict_customer(customer):
    response = requests.post(url, json=customer).json()
    print(response)

    if response['churn'] == True:
        print('sending promo email to %s' % customer_id)
    else:
        print('not sending promo email to %s' % customer_id)

predict_customer(customer)
customer['tenure'] = 12
customer['totalcharges'] = customer.get('totalcharges', 0) * 12
predict_customer(customer)
