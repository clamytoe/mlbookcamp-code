from os import environ

import requests
from dotenv import load_dotenv

load_dotenv()


def main():
    # url = "http://localhost:8080/2015-03-31/functions/function/invocations"
    url = environ.get("aws_lambda_uri")
    data = {"url": "http://bit.ly/mlbookcamp-pants"}

    if url is not None:
        result = requests.post(url, json=data).json()
        print(result)
    else:
        print("Unable to load environment variables")


if __name__ == "__main__":
    main()
