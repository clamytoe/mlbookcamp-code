from hashlib import sha1


def compute_hash(email):
    return sha1(email.lower().encode('utf-8')).hexdigest()


if __name__ == '__main__':
    email = 'clamytoe@gmail.com'
    print(compute_hash(email))
