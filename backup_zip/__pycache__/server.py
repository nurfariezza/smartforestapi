from flask import Flask, request,jsonify,session,g
from flask_restful import Resource, Api,reqparse
from dbhelper import initdb
from models import TLogin
import mysql.connector,json
import models,logging
from resourceapi import resourceapi
from flask_httpauth import HTTPBasicAuth
from cheroot.wsgi import Server as WSGIServer
from security import authenticate, identity
from flask_jwt import jwt_required,JWT
from flask_session import Session
import jwt,hashlib
from validate import validate_email_and_password, validate_user_form
from user import User
from datetime import datetime, timedelta
import getpass
import redis
from utils import UIException

app = Flask(__name__)
logging.basicConfig(filename='frimapi.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.secret_key ='secret@@RT@^FRIM'
api = Api(app, prefix="/apipy/v1")

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://10.80.10.39:6379')
app.config["REDIS_URL"] = "redis://10.80.10.39:6379"
app.config['SESSION_TYPE'] = "redis"




auth = HTTPBasicAuth()

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

class Login(Resource):
    def post(self,data=auth):
        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            is_validated = validate_email_and_password(data.get('email'), data.get('password'))
            if is_validated is not True:
                return dict(status=0, message='Invalid data', data=None, error=is_validated)
            

            password_decr = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()
            user = User().login(data["email"],password_decr)
            print(user)
           
            if user['status'] != 1: 
                print("error: Invalid Login",user)
                return user
            else:
                session['user'] =user['data'][0]['email']

            return jsonify(user)
        except Exception as e:
            print(e)


class UserList(Resource):

    def get(self):
        if g.user is None:            
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            

            return data
        con, cur = initdb()
        try:
            q = """
                SELECT user.email,user.username, user.is_approval, user_cate.group_id, user_cate.group, role.role_id, role.role_name FROM user, role, user_cate WHERE role.role_id =user.roleid and user_cate.group_id = user.group_id
                """

            cur.execute(q,)
            user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            print(g.user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user
                    }
                return user
        except Exception as e:
            print("1b")
            print(e)

        return user

class Profile(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            

            return data
        con, cur = initdb()
        try:
            q = """
                SELECT user.email,user.username, user.is_approval, user_cate.group_id, user_cate.group, role.role_id, role.role_name FROM user, role, user_cate WHERE role.role_id =user.roleid and user_cate.group_id = user.group_id and user.email=%s
            
                """
            data = (g.user,)
            cur.execute(q,data)
            user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            print(g.user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user
                    }
                return user
        except Exception as e:
            print("1b")
            print(e)

        return user

class CreateUser(Resource):
    
    def post(self):
        if g.user is None:
            return {"Authentication Failed.Kindly login again"}, 400

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            is_validated = validate_user_form(data.get('username'),data.get('email'), data.get('password'),data.get('role'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            userinfo = User().add_newuser(
                data["username"],
                data["email"],
                data["contactno"]
            )
            return jsonify(userinfo)
        except Exception as e:
            print(e)


class  DestroySession(Resource):   
    def get(self):
        if 'user' in session:
            session.pop('user', None)
            data = {
                "status": 1,
                "data": "You successfully logged out"
                }
            return data
        

# class UserInfo(Resource):
#     def get(self,userid):
#         if g.user is None:
#             return {"Authentication Failed.Kindly login again"}, 400

#         con, cur = initdb()
#         try:
#             q = """
#                 select * from user where userid =%s
            
#                 """
#             data = (userid,)
#             cur.execute(q, data)
#             user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

#             if user:
#                 return user
#             else:
#                 return ("message:No User Found")
#         except Exception as e:
#             print("1b")
#             print(e)

#         return user


# share API Web and Mobile
class  RoleList(Resource):
    def get(self):
        con, cur = initdb()
        try:
            q = """
                SELECT  role_id, role_name FROM role
            
                """

            cur.execute(q,)
            role = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            
            if not role or None:
                role = {
                        "status": 0,
                        "data": 'Data not Found'
                    }
            
            else:
                role = {
                        "status": 1,
                        "data": role
                    }

            return role
        except Exception as e:
            print(e)

        return role


# start API for Web

class UserListw(Resource):
    def get(self):
        con, cur = initdb()
        try:
            q = """
                SELECT  user.email,user.username, role.role_name, user_cate.group, user.contactno FROM user, role, user_cate WHERE role.role_id =user.roleid and user_cate.cat_id = user.cat_id 
            
                """
            cur.execute(q,)
            user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            print(g.user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user
                    }
                return user
        except Exception as e:
            print("1b")
            print(e)

        return user

class CreateUserw(Resource):
    def post(self):
        # if g.user is None:
        #     return {"Authentication Failed.Kindly login again"}, 400
        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            # validate input
            is_validated = validate_user_form(data.get('username'),data.get('email'), data.get('password'),data.get('contactno'),data.get('is_approval'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            userinfo = User().add_newuser(
                data["username"],
                data["password"],
                data["contactno"],
                data["email"],
                data["is_approval"]
            )
            # verify(data["email"],data["password"])
            return jsonify(userinfo)
        except Exception as e:
            print(e)




# api.add_resource(Login, '/users/login/' )
# api.add_resource(UserList, '/userlist/')
# api.add_resource(CreateUser, '/adduser/')
# api.add_resource(DestroySession, '/logout/' )
# api.add_resource(UserInfo, '/user/<userid>')
# api.add_resource(Test, '/test/' )
# api.add_resource(RoleList, '/role/' )


api.add_resource(Login, '/m/users/login/' )
api.add_resource(UserList, '/m/userlist/')
api.add_resource(Profile, '/m/profile/')
api.add_resource(DestroySession, '/m/logout/' )
# api.add_resource(UserInfo, '/m/user/<userid>')



# api for web
api.add_resource(UserListw, '/w/userlist/')
api.add_resource(CreateUserw, '/w/adduser/')

#both 
api.add_resource(RoleList, '/wm/role/')

#server = WSGIServer(bind_addr=('0.0.0.0', int(5050)), wsgi_app=app, numthreads=100)
#try:
#    server.start()
#except KeyboardInterrupt:
#    server.stop()

if __name__ == '__main__':
    app.run(debug=True, port=8000)
    



