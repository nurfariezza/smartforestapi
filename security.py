from hmac import compare_digest
from forest import Forest




def authenticate(username, password):
    user = Forest.find_by_username(username)
    print(user)
    if user and compare_digest(user.password, password):
        # print(user.password)
        print(user)
        return user


def identity(payload):
    user_id = payload['identity']
    return Forest.find_by_id(user_id)
