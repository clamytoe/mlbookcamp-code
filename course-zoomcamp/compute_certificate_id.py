from hashlib import sha1


def compute_hash(email):
    return sha1(email.encode("utf-8")).hexdigest()


def compute_certificate_id(email):
    email_clean = email.lower().strip()
    return compute_hash(email_clean + "_")


def main():
    email = "clamytoe@gmail.com"
    cohort = 2022
    course = "ml-zoomcamp"
    your_id = compute_certificate_id(email)
    url = f"https://certificate.datatalks.club/{course}/{cohort}/{your_id}.pdf"
    print(url)


if __name__ == "__main__":
    main()
