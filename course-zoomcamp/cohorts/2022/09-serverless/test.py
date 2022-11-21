import requests


def main():
    url = "http://localhost:8080/2015-03-31/functions/function/invocations"
    data = {
        "url": "https://upload.wikimedia.org/wikipedia/en/e/e9/GodzillaEncounterModel.jpg"
    }

    result = requests.post(url, json=data).json()
    print(result)


if __name__ == "__main__":
    main()
