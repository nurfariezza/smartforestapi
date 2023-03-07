from hmac import compare_digest
from user import User




def authenticate(username, password):
    user = User.find_by_username(username)
    print(user)
    if user and compare_digest(user.password, password):
        # print(user.password)
        print(user)
        return user


def identity(payload):
    user_id = payload['identity']
    return User.find_by_id(user_id)
