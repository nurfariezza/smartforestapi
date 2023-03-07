from flask import Flask, request,jsonify,session,g
from flask_restful import Resource, Api,reqparse
from dbhelper import initdb
from models import TLogin
import mysql.connector,json
import models,logging
from flask_httpauth import HTTPBasicAuth
from cheroot.wsgi import Server as WSGIServer
from security import authenticate, identity
from flask_jwt import jwt_required,JWT
from flask_session import Session
import jwt,hashlib
from validate import validate_email_and_password, validate_user_form,validate_penandaan_semp_form,validate_createkompatmen,validate_createfamilyspesis,validate_createsubspesis,validate_createhutan,validate_bancian_pre_tebangan,validate_add_rawatan,validate_penandaanpokok,validate_banciantinggal,validate_pembalakaddTual,validate_price_data,validate_bancian_selepas_tebangan,validate_update_penandaanpokok,validate_body_value
from forest import Forest
from datetime import datetime, timedelta
import getpass
import redis
from utils import UIException
import requests
from firebase_admin import auth
import firebase_admin
from firebase_admin import credentials, messaging
import os

app = Flask(__name__)
logging.basicConfig(filename='frimapi.log', level=logging.ERROR, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
app.secret_key ='secret@@RT@^FRIM'
api = Api(app, prefix="/apipy/v1")

app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['SESSION_REDIS'] = redis.from_url('redis://10.80.10.39:6379')
app.config["REDIS_URL"] = "redis://10.80.10.39:6379"
app.config['SESSION_TYPE'] = "redis"

script_dir = os.path.dirname(__file__)
current_file = os.path.abspath("frimapi-5b83db16e9c8.json")
print(current_file)
firebase_cred = credentials.Certificate(current_file)

firebase_app = firebase_admin.initialize_app(firebase_cred)

auth = HTTPBasicAuth()

@app.before_request
def before_request():
    g.user = None
    g.u_id = None
    if 'user' in session:
        g.user = session['user']
        # g.u_id = session['user_data']
    if 'user_data' in session:
        g.u_id = session['user_data']['data'][0]['u_id']
        # print(g.u_id)


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
            user = Forest().login(data["email"],password_decr)
        #    / print(user)
           
            if user['status'] != 1: 
                print("error: Invalid Login",user)
                return user
            else:
                session['user'] =user['data'][0]['email']
                session['user_data'] = user
                # print(session['userdata'])

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

            user= Forest().get_userlist()
            # print(user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user,

                    }
                return user
        except Exception as e:
            print(e)


class Profile(Resource):
    def get(self,userid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            user= Forest().profile(userid)
            # print(user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                site = Forest().get_default_site(data["email"])
                user = {
                        "status": 1,
                        "data": user,
                        "site": site

                    }
                return user
        except Exception as e:
            print(e)

        return user



class getSite(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            user= Forest().get_site()
            # print(user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user,

                    }
                return user
        except Exception as e:
            print(e)



class getHutan(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            user= Forest().get_hutan_list()
            print(user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user,

                    }
                return user
        except Exception as e:
            print(e)



class getHutanDetail(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            hutan= Forest().get_hutan_detail()
            if not hutan or None:
                hutan = {
                        "status": 0,
                        "data": 'No Record'
                    }
            else:
                hutan = {
                        "status": 1,
                        "data": hutan,

                    }
            return hutan
        except Exception as e:
            print(e)



class CreateUser(Resource):
    
    def post(self):
        if g.user is None:
            data = {
                "status": 0
                ,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            print(data)
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            # defpassword ="P@ssw0rd2288"
            is_validated = validate_user_form(data.get('username'),data.get('password'),data.get('email'), data.get('siteid'),data.get('group_id'))
            password_decr = hashlib.sha256(data.get('password').encode('utf-8')).hexdigest()

            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400
            # print(session['user'])
            user_id = session['user_data']['data'][0]['u_id']

            userinfo = Forest().create_user(
                data["username"],
                password_decr,  
                data["email"], 
                data["is_approval"],       
                data["group_id"],
                data["is_admin"],
                data["contactno"],
                data["siteid"], 
                data["access_role"],
                user_id
                
                
            )
            return jsonify(userinfo)
        except Exception as e:
            print(e)


class getUser(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            user= Forest().get_userprofile_email(g.user)
            # print(user)
            if not user or None:
                user = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return user
            else:
                user = {
                        "status": 1,
                        "data": user,

                    }
                return user
        except Exception as e:
            print(e)



class UpdateUser(Resource):
    def post(self,userid):
        if g.user is None:
            data = {
                "status": 0
                ,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            print(data)
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            # password_decr = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()

            userinfo = Forest().update_user(userid,
                data["email"],
                data["username"], 
                data["contactno"],   
                data["siteid"],        
                data["is_approval"],             
                data["group_id"],
                data["is_admin"],
                data["access_role"],
                session['user']
                
            )

            
                
            return jsonify(userinfo)
        except Exception as e:
            print(e)


class ResetPassword(Resource):
    def post(self,userid):
        if g.user is None:
            data = {
                "status": 0
                ,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            print(data)
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            password_decr = hashlib.sha256(data["password"].encode('utf-8')).hexdigest()

            userinfo = Forest().reset_password(userid,
                data["email"],
                password_decr,
                session['user']
                
            )

            
                
            return jsonify(userinfo)
        except Exception as e:
            print(e)



class DeleteUser(Resource):
    def post(self,userid):
        if g.user is None:
            data = {
                "status": 0
                ,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            userinfo = Forest().delete_user(userid)
            return jsonify(userinfo)
        except Exception as e:
            print(e)





class  DestroySession(Resource):   
    def get(self):
        if 'user' in session:
            print(session)
            
            session.pop('user', None)
            data = {
                "status": 1,
                "data": "You successfully logged out"
                }
            return data
        


class UserListw(Resource):
    def get(self):
        con, cur = initdb()
        try:
            q = """
                SELECT  user.email,user.username, role.role_name, access_group.group, user.contactno FROM user, role, access_group WHERE role.role_id =user.roleid and access_group.cat_id = user.cat_id 
            
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



class PenandaanSempKompartmen(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_penandaan_semp_form(data.get('hutansimpan_id'),data.get('kompatmen'), data.get('pokokstesen'),data.get('spesies'))
            # print(data)
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_penandaansempkompartmen = Forest().post_penandaansempkompartmen(
                data["hutansimpan_id"], 
                data["kompatmen"],                        
                data["fromt"],               
                data["pokokstesen"],
                data["spesies"],
                data["dbh"],
                data["bearing"],
                data["jarak"],
                data["koordinate_x"],
                data["koordinate_y"]
            )
            return jsonify(post_penandaansempkompartmen)
        except Exception as e:
            print(e)


class UpdatePenandaanSempKompartmen(Resource):
    def post(self, point_id):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_penandaan_semp_form(data.get('hutansimpan_id'),data.get('kompatmen'), data.get('pokokstesen'),data.get('spesies'))
            # print(data)
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_penandaansempkompartmen = Forest().update_penandaansempkompartmen(
                data["hutansimpan_id"], 
                data["kompatmen"],                        
                data["fromt"],               
                data["pokokstesen"],
                data["spesies"],
                data["dbh"],
                data["bearing"],
                data["jarak"],
                data["koordinate_x"],
                data["koordinate_y"],
                point_id
            )
            return jsonify(post_penandaansempkompartmen)
        except Exception as e:
            print(e)



class CreateKompatmen(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_createkompatmen(data.get('name_code'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_penandaansempkompartmen = Forest().create_kompatmen(
                data["hutan_id"], 
                data["persempadanan_id"], 
                data["keluasan"],                        
                data["kelas_hutan"],
                data["aktiviti_pengurusan_id"],
                data["name_code"]
               
            )
            return jsonify(post_penandaansempkompartmen)
        except Exception as e:
            print(e)


class CreateHutanSimpan(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            print(data)
            is_validated = validate_createhutan(data.get('state'),data.get('district'),data.get('type'),data.get('name'),data.get('keluasan'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            create_hutan_post = Forest().create_hutan(
                data["state"], 
                data["district"],                        
                data["type"],
                data["name"],
                data["keluasan"],
                data["kelas_hutan"]
            )
            return jsonify(create_hutan_post)
        except Exception as e:
            print(e)


class getKompatmen(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kompatmentlist= Forest().get_kompatmen_list()
            if not kompatmentlist or None:
                kompatmentlist = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return kompatmentlist
            else:
                kompatmentlist = {
                        "status": 1,
                        "data": kompatmentlist,

                    }
                return kompatmentlist
        except Exception as e:
            print(e)



class getKompatmenByHutan(Resource):
    def get(self,hutanid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kompatmentlist= Forest().get_kompatmen_byhutan(hutanid)
            if not kompatmentlist or None:
                kompatmentlist = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return kompatmentlist
            else:
                kompatmentlist = {
                        "status": 1,
                        "data": kompatmentlist,

                    }
                return kompatmentlist
        except Exception as e:
            print(e)





class getKerosakan_List(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_kerosakan= Forest().get_jenis_kerosakan()
            if not get_kerosakan or None:
                get_kerosakan = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_kerosakan
            else:
                get_kerosakan = {
                        "status": 1,
                        "data": get_kerosakan,

                    }
                return get_kerosakan
        except Exception as e:
            print(e)

class getRawatan_List(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_rawatan= Forest().get_jenis_rawatan()
            if not get_rawatan or None:
                get_rawatan = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_rawatan
            else:
                get_rawatan = {
                        "status": 1,
                        "data": get_rawatan,

                    }
                return get_rawatan
        except Exception as e:
            print(e)



class getTahap_Kerosakan(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_kerosakan= Forest().get_tahap_kerosakan()
            if not get_kerosakan or None:
                get_kerosakan = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_kerosakan
            else:
                get_kerosakan = {
                        "status": 1,
                        "data": get_kerosakan,

                    }
                return get_kerosakan
        except Exception as e:
            print(e)




class getCheckKoordinate(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            getkoordinate= Forest().get_last_koordinate(kompatmenid)
            print(getkoordinate)

            if not getkoordinate or None:
                getkoordinate = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return getkoordinate
            else:
                getkoordinate = {
                        "status": 1,
                        "data": getkoordinate,

                    }
                return getkoordinate
        except Exception as e:
            print(e)

class getSempadanList(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            list_sempadan_koordinate= Forest().get_list_sempadan_koordinate(kompatmenid)
            if not list_sempadan_koordinate or None:
                list_sempadan_koordinate = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return list_sempadan_koordinate
            else:
                list_sempadan_koordinate = {
                        "status": 1,
                        "data": list_sempadan_koordinate,

                    }
                return list_sempadan_koordinate
        except Exception as e:
            print(e)




class getSpesies_Type(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            spesies_type= Forest().get_spesies_type()
            if not spesies_type or None:
                spesies_type = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return spesies_type
            else:
                spesies_type = {
                        "status": 1,
                        "data": spesies_type,

                    }
                return spesies_type
        except Exception as e:
            print(e)



class getSpesies_Kump(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kump_spesies= Forest().get_kump_spesies()
            if not kump_spesies or None:
                kump_spesies = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return kump_spesies
            else:
                kump_spesies = {
                        "status": 1,
                        "data": kump_spesies,

                    }
                return kump_spesies
        except Exception as e:
            print(e)

class CreateFamilySpesis(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_createfamilyspesis(data.get('name'),data.get('kumpulan_d_nd'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_familyspesies = Forest().create_familyspesies(
                data["name"], 
                data["kumpulan_d_nd"]               
                
               
            )
            # print(post_familyspesies)
            return jsonify(post_familyspesies)
        except Exception as e:
            print(e)


class CreateSubSpesis(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_createsubspesis(data.get('family_id'),data.get('local_name'),data.get('scientific_name'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_familyspesies = Forest().create_subspesies(
                data["family_id"],                      
                data["local_name"],
                data["scientific_name"],
                data["kumpulan_7"]
               
            )
            return jsonify(post_familyspesies)
        except Exception as e:
            print(e)



class getFamily_Spesies(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kump_spesies= Forest().get_family_spesies()
            if not kump_spesies or None:
                kump_spesies = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return kump_spesies
            else:
                kump_spesies = {
                        "status": 1,
                        "data": kump_spesies,

                    }
                return kump_spesies
        except Exception as e:
            print(e)



class getSpesies_List(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kump_spesies= Forest().getspesies_list()
            if not kump_spesies or None:
                kump_spesies = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return kump_spesies
            else:
                kump_spesies = {
                        "status": 1,
                        "data": kump_spesies,

                    }
                return kump_spesies
        except Exception as e:
            print(e)



class BancianSebelumTebangan(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            # check pokok id exist in pokok table.if no, proceed
            is_pokok_exist = Forest().validate_is_pokok_exist(data["no_pokok"])
            if is_pokok_exist is True:
                return dict(message='Pokok ID Already Exist in Database', data=None, error=data["no_pokok"]), 400

            # check pokok id exist in pre bancian.
            pokok_id = Forest().validate_pokokid(data["no_pokok"])
            if pokok_id is True:
                return dict(message='Duplicate Pokok ID', data=None, error=pokok_id), 400

            is_validated = validate_bancian_pre_tebangan(data.get('kompatmen_id'),data.get('no_pokok'),data.get('dbh'),data.get('spesies'),data.get('pepanjat'),data.get('bil_tual'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_bancian_pre_tebangan = Forest().bancian_pre_tebangan(
                data["kompatmen_id"], 
                data["no_pokok"],                        
                data["dbh"],
                data["spesies"],
                data["pepanjat"],
                data["bil_tual"]
               
            )
            return jsonify(post_bancian_pre_tebangan)
        except Exception as e:
            print(e)



class UpdateBancianSebelumTebangan(Resource):
    def post(self,pokokid):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            # check pokok id exist in pokok table.if no, proceed
            is_pokok_exist = Forest().validate_is_pokok_exist(data["no_pokok"])
            if is_pokok_exist is not True:
                return dict(message='Pokok ID Not Exist in Database', data=None, error=data["no_pokok"]), 400

            # check pokok id exist in pre bancian.
            pokok_id = Forest().validate_pokokid(data["no_pokok"])
            if pokok_id is not True:
                return dict(message='Pokok ID Not Exist in Database', data=None, error=pokok_id), 400

            
            post_bancian_pre_tebangan = Forest().update_bancian_pre_tebangan(
                data["kompatmen_id"], 
                data["no_pokok"],                        
                data["dbh"],
                data["spesies"],
                data["pepanjat"],
                data["bil_tual"]
               
            )
            return jsonify(post_bancian_pre_tebangan)
        except Exception as e:
            print(e)


class AddRawatan(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_validated = validate_add_rawatan(data.get('kompatmen_id'),data.get('jenis_rawatan'),data.get('tahun'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            add_rawatan = Forest().add_rawatan(
                data["kompatmen_id"], 
                data["jenis_rawatan"],                        
                data["tahun"]
               
            )
            return jsonify(add_rawatan)
        except Exception as e:
            print(e)


class PenandaanPokok(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            is_validated = validate_penandaanpokok(data.get('kompatmen_id'),data.get('no_pokok'),data.get('no_tag'),data.get('spesies_id'),data.get('dbh'),data.get('bil_tual'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            # check NFC id exist in pokok table.if no, procees with penandaanpokok
            nfc_id = Forest().validate_nfcid(data["no_tag"])
            if nfc_id is True:
                return dict(message='Duplicate NFC ID', data=None, error=nfc_id), 400

            # check pokok id exist in pokok table.
            is_pokok_id = Forest().validate_is_pokok_exist(data["no_pokok"])
            if is_pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=is_pokok_id), 400

            # check pokok id exist in pre bancian.if yes, procees with penandaanpokok.
            pokok_id = Forest().validate_pokokid(data["no_pokok"])
            if pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=pokok_id), 400
            
            post_penandaan_pokok = Forest().penandaan_pokok(
                data["kompatmen_id"], 
                data["no_pokok"],  
                data["no_tag"],                      
                data["spesies_id"],
                data["dbh"],
                data["koordinate_x"],
                data["koordinate_y"],
                data["bil_tual"]
            
            )
            return jsonify(post_penandaan_pokok)
        except Exception as e:
            print(e)




class Update_PenandaanPokok(Resource):
    def post(self,nfctag):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            is_validated = validate_update_penandaanpokok(data.get('kompatmen_id'),data.get('spesies_id'),data.get('dbh'),data.get('bil_tual'),data.get('no_pokok'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400
      
            post_penandaan_pokok = Forest().update_penandaan_pokok(nfctag,
                data["kompatmen_id"],
                data["no_pokok"],                     
                data["spesies_id"],
                data["dbh"],
                data["koordinate_x"],
                data["koordinate_y"],
                data["bil_tual"]
                
            
            )
            return jsonify(post_penandaan_pokok)
        except Exception as e:
            print(e)




class PostBancianTinggal(Resource):
    def post(self,nfctag):
        # no_tag = nfctag
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400
            # is_validated = validate_banciantinggal(data.get('no_pokok'),data.get('dbh'),data.get('status_pokok'),data.get('jenis_kerosakan'),data.get('tahap_kerosakan'))
            # if is_validated is not True:
            #     return dict(message='Invalid data', data=None, error=is_validated), 400

            # check pokok id exist in banciantinggal.
            pokok_id = Forest().validate_pokokid_stok_dirian_tinggal(data["no_pokok"])
            if pokok_id is True:
                return dict(message='Duplicate Pokok ID', data=None, error=pokok_id), 400

            bancian_dirian_tinggal = Forest().add_bancian_dirian_tinggal(
                data["no_pokok"], 
                data["no_tag"],
                data["dbh"], 
                data["status_pokok"],
                data["jenis_kerosakan"],
                data["tahap_kerosakan"]
               
            )
            return jsonify(bancian_dirian_tinggal)
        except Exception as e:
            print(e)




class getBancianTinggal(Resource):
    def get(self,nfctag):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_bancian_dirian_tinggal(nfctag)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)


# getkomptment detail for dashboard
class getKompatmenDetailDashboard(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            kompatmentinfo= Forest().get_kompatmen_detail_dashboard(kompatmenid)
            if not kompatmentinfo or None:
                kompatmentinfo = {
                        "status": 0,
                        "data": 'No Record'
                    }
            else:
                kompatmentinfo = {
                        "status": 1,
                        "data": kompatmentinfo,

                    }
            return kompatmentinfo
        except Exception as e:
            print(e)





class Pembalak_Post_Pengeluaran(Resource):
    def post(self,nfctag):
        # no_tag = nfctag
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide complete information",
                    "data": None,
                    "error": "Bad request"
                }, 400
            is_validated = validate_pembalakaddTual(data.get('no_pokok'),data.get('nfc_tag'),data.get('no_tual'),data.get('panjang'),data.get('dbh'))
            if is_validated is not True:
                return dict(message="Please provide complete information", data=None, error=is_validated), 400
           
            if nfctag != data.get('nfc_tag'):
                return dict(message="Please enter correct NFC Number", data=None), 400
            
            pembalak_add_tual = Forest().Pembalak_Post_Tual_PengeluaranSebenar(
                data["no_pokok"], 
                data["nfc_tag"],
                data["no_tual"], 
                data["panjang"],
                data["dbh"]

               
            )
            return jsonify(pembalak_add_tual)
        except Exception as e:
            print(e)



# get for proses pembalakan -
class Pembalak_getPengeluaranSebenar(Resource):
    def get(self,nfctag):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            get_pembalak_pengeluaran= Forest().get_pembalak_pengeluaran(nfctag)

            if not get_pembalak_pengeluaran or None:
                get_pembalak_pengeluaran = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_pembalak_pengeluaran
            else:
                get_pembalak_pengeluaran = {
                        "status": 1,
                        "data": get_pembalak_pengeluaran,

                    }
                return get_pembalak_pengeluaran
        except Exception as e:
            print(e)



class Add_Spesies_PriceList(Resource):
    def post(self):
        # no_tag = nfctag
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide complete information",
                    "data": None,
                    "error": "Bad request"
                }, 400
            is_validated = validate_price_data(data.get('spesies_id'),data.get('price'))
            if is_validated is not True:
                return dict(message="Please provide complete information", data=None, error=is_validated), 400
           
            user_id = session['user_data']['data'][0]['u_id']
            add_price = Forest().Add_pricelist(
                data["spesies_id"], 
                data["price"],
                user_id
                
               
            )
            return jsonify(add_price)
        except Exception as e:
            print(e)


class BancianSelepasTebangan(Resource):
    def post(self,nfctag):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400



            is_validated = validate_bancian_selepas_tebangan(data.get('kompatmen_id'),data.get('no_pokok'),data.get('no_tag'),data.get('dbh'),data.get('spesies'),data.get('bil_tual'))
            if is_validated is not True:
                return dict(message='Invalid data', data=None, error=is_validated), 400

            post_bancian_tebangan = Forest().bancian_selepas_tebangan(
                data["kompatmen_id"], 
                data["no_pokok"], 
                data["no_tag"],                       
                data["dbh"],
                data["spesies"],
                data["pepanjat"],
                data["bil_tual"]
               
            )
            return jsonify(post_bancian_tebangan)
        except Exception as e:
            print(e)



class getBancianSelepasTebangan(Resource):
    def get(self,nfctag):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_post_tebangan= Forest().get_bancian_selepas_tebangan(nfctag)

            if not get_post_tebangan or None:
                get_post_tebangan = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_post_tebangan
            else:
                get_post_tebangan = {
                        "status": 1,
                        "data": get_post_tebangan,

                    }
                return get_post_tebangan
        except Exception as e:
            print(e)

# get for proses pembalakan -
class BancianSebelumTebangan_List(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            sebelum_tebangan_list= Forest().get_bancian_sebelum_tebangan(kompatmenid)

            if not sebelum_tebangan_list or None:
                sebelum_tebangan_list = {
                        "status": 0,
                        "data": 'No Record'
                    }
            else:
                sebelum_tebangan_list = {
                        "status": 1,
                        "data": sebelum_tebangan_list,

                    }
            return sebelum_tebangan_list
        except Exception as e:
            print(e)


# get for DashboardList - Had Pengeluaran Sebenar
class DashboardHadPengeluaranSebenar_List(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            pengeluaransebenar_list= Forest().get_pengeluaransebenar_list_dashboard(kompatmenid)

            if not pengeluaransebenar_list or None:
                pengeluaransebenar_list = {
                        "status": 0,
                        "data": 'No Record'
                    }
            else:
                pengeluaransebenar_list = {
                        "status": 1,
                        "data": pengeluaransebenar_list,

                    }
            return pengeluaransebenar_list
        except Exception as e:
            print(e)


# dashboard list
class getBancianTinggalDashboard_List(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_bancian_dirian_tinggal_dashboard(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)

# dashboard list
class DashboardSelepasTebangan_List(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_bancianselepastebangan_list_dashboard(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)

# dashboard list
class DashboardPokokTebang_List(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_senaraipokoktebang_list_dashboard(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)

# dashboard list
class DashboardPokokTebang_Detail(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_senaraipokoktebang_detaillist_dashboard(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)


class Add_Tual(Resource):
    def post(self):
        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide complete information",
                    "data": None,
                    "error": "Bad request"
                }, 400
   
            is_pokok_exist = Forest().validate_is_pokok_exist(data["pokok_id"])
            if is_pokok_exist is not True:
                return dict(message='No Record Found', data=None, error=data["pokok_id"]), 400

            user_id = session['user_data']['data'][0]['u_id']

            add_tual = Forest().pembalak_add_tual(
                data["bil_tual"], 
                data["pokok_id"],
                data["remark"],
                user_id
                
               
            )
            return jsonify(add_tual)
        except Exception as e:
            print(e)


class Approval_all_list(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            pending_list_tual= Forest().get_all_list()

            if not pending_list_tual or None:
                pending_list_tual = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return pending_list_tual
            else:
                pending_list_tual = {
                        "status": 1,
                        "data": pending_list_tual,

                    }
                return pending_list_tual
        except Exception as e:
            print(e)

class Approval_pending_list(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            pending_list_tual= Forest().get_pending_list()

            if not pending_list_tual or None:
                pending_list_tual = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return pending_list_tual
            else:
                pending_list_tual = {
                        "status": 1,
                        "data": pending_list_tual,

                    }
                return pending_list_tual
        except Exception as e:
            print(e)

class Approval_approve_list(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            approve_list_tual= Forest().get_approved_list()

            if not approve_list_tual or None:
                approve_list_tual = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return approve_list_tual
            else:
                approve_list_tual = {
                        "status": 1,
                        "data": approve_list_tual,

                    }
                return approve_list_tual
        except Exception as e:
            print(e)

class Approval_reject_list(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            reject_list_tual= Forest().get_reject_list()

            if not reject_list_tual or None:
                reject_list_tual = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return reject_list_tual
            else:
                reject_list_tual = {
                        "status": 1,
                        "data": reject_list_tual,

                    }
                return reject_list_tual
        except Exception as e:
            print(e)


# action req to pembalak-addtual
class Pegawai_Action_on_Request(Resource):
    def post(self,pokokid):

        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            # if pokokid!=data.get('pokok_id'):
            #     return dict(message='Mismatch Pokok ID', data=None, error=pokokid), 400

            # check pokok id exist in pokok table.
            is_pokok_id = Forest().validate_is_pokok_exist(data.get('pokok_id'))
            if is_pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=is_pokok_id), 400

            user_id = session['user_data']['data'][0]['u_id']

            post_pegawai_action = Forest().pegawai_approve_add_tual_request(
                data["pokok_id"], 
                data["tual_lama"],
                data["tual_tambahan"],                       
                data["status"],
                user_id
                              
            )
            return jsonify(post_pegawai_action)
        except Exception as e:
            print(e)




# get for proses Pengeluaran Sebenar -Pegawai
class Pegawai_getPengeluaranSebenar(Resource):
    def get(self,nfctag):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            get_pegawai_pengeluaran= Forest().get_pegawai_pengeluaranSebenar_cukai(nfctag)

            if not get_pegawai_pengeluaran or None:
                get_pegawai_pengeluaran = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_pegawai_pengeluaran
            else:
                get_pegawai_pengeluaran = {
                        "status": 1,
                        "data": get_pegawai_pengeluaran,

                    }
                return get_pegawai_pengeluaran
        except Exception as e:
            print(e)

class Pegawai_Confirm_Tual_price(Resource):
    def post(self,nfctag):

        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_pokok_id = Forest().validate_is_pokok_exist(data.get('pokok_id'))
            if is_pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=is_pokok_id), 400

            user_id = session['user_data']['data'][0]['u_id']

            post_pegawai_action = Forest().pegawai_confirm_tual_price(
                data["nfctag"],
                data["pokok_id"], 
                data["spesies_id"], 
                data["diameter"],    
                data["price_id"],                  
                data["price"],
                user_id
                              
            )
            return jsonify(post_pegawai_action)
        except Exception as e:
            print(e)

class Pegawai_Action_on_Final_price(Resource):
    def post(self,nfctag):

        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400


            is_pokok_id = Forest().validate_is_pokok_exist(data.get('pokok_id'))
            if is_pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=is_pokok_id), 400

            user_id = session['user_data']['data'][0]['u_id']

            post_pegawai_action = Forest().pegawai_approve_reject_price(
                data["nfctag"],
                data["pokok_id"],                    
                data["price"],
                data["status"],
                user_id
                              
            )
            return jsonify(post_pegawai_action)
        except Exception as e:
            print(e)


class Pembalak_is_open(Resource):
    def post(self,pokokid):

        if g.user is None:
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }   
            return data         

        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide user details",
                    "data": None,
                    "error": "Bad request"
                }, 400

            # if pokokid!=data.get('pokok_id'):
            #     return dict(message='Mismatch Pokok ID', data=None, error=pokokid), 400

            # check pokok id exist in pokok table.
            is_pokok_id = Forest().validate_is_pokok_exist(data.get('pokok_id'))
            if is_pokok_id is not True:
                return dict(message='Invalid Pokok ID', data=None, error=is_pokok_id), 400

            user_id = session['user_data']['data'][0]['u_id']

            post_pembalak_action = Forest().pembalak_is_open_noti(
                data["pokok_id"], 
                data["bil_tual"], 
                data["status"],
                user_id
                              
            )
            return jsonify(post_pembalak_action)
        except Exception as e:
            print(e)


class Pembalak_unread_Notification(Resource):
    def get(self):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            get_unread_noti= Forest().pembalak_unread_notification_list()

            if not get_unread_noti or None:
                get_unread_noti = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_unread_noti
            else:
                get_unread_noti = {
                        "status": 1,
                        "data": get_unread_noti,

                    }
                return get_unread_noti
        except Exception as e:
            print(e)



class DashboardPokok_map_dip(Resource):
    def get(self,kompatmenid):

        # if g.user is None:            
   
        #     data = {
        #         "status": 0,
        #         "data": "Authentication Failed.Kindly login again"
        #         }            
            
        #     return data
          
        con, cur = initdb()
        try:

            get_pokok_list_Dip= Forest().pokok_list_Dip(kompatmenid)

            if not get_pokok_list_Dip or None:
                get_pokok_list_Dip = {
                        "data": 'No Record'
                    }
                return get_pokok_list_Dip
            else:
                get_pokok_list_Dip = {
                        "data": get_pokok_list_Dip,

                    }
                return get_pokok_list_Dip
        except Exception as e:
            print(e)


class DashboardPokok_map_nondip(Resource):
    def get(self,kompatmenid):

        # if g.user is None:            
   
        #     data = {
        #         "status": 0,
        #         "data": "Authentication Failed.Kindly login again"
        #         }            
            
        #     return data
          
        con, cur = initdb()
        try:

            get_pokok_list_NonDip= Forest().pokok_list_NonDip(kompatmenid)

            if not get_pokok_list_NonDip or None:
                get_pokok_list_NonDip = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_pokok_list_NonDip
            else:
                get_pokok_list_NonDip = {
                        "status": 1,
                        "data": get_pokok_list_NonDip,

                    }
                return get_pokok_list_NonDip
        except Exception as e:
            print(e)

class Get_Latest_Price_spesies(Resource):
    def get(self,spesiesid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_price_list= Forest().get_latest_price_byspesies(spesiesid)

            if not get_price_list or None:
                get_price_list = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_price_list
            else:
                get_price_list = {
                        "status": 1,
                        "data": get_price_list,

                    }
                return get_price_list
        except Exception as e:
            print(e)


class Pembalak_Noti(Resource):

    def post(self):
       
        con, cur = initdb()


        try:
            data = request.json
            if not data:
                return {
                    "message": "Please provide body details",
                    "data": None,
                    "error": "Bad request"
                }, 400
           
            title=(data.get('title'))
            bodydetail=(data.get('body'))

            topic = 'frimnotify'
            message = messaging.Message(
            notification=messaging.Notification(

            title=title,
            body=bodydetail
            ),
            topic=topic
            )
            res= messaging.send(message)
            
            print(res)
            return {
                    "status": 1,
                    "data": "Notification Send"
                } 
        except Exception as e:
            print(e)



# get for DashboardList - Had Pengeluaran Sebenar
class DashboardHadPengeluaranSebenar_ViewDetail(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:
            
            pengeluaransebenar_list= Forest().get_pengeluaransebenar_list_dashboard_viewdetail(kompatmenid)

            if not pengeluaransebenar_list or None:
                pengeluaransebenar_list = {
                        "status": 0,
                        "data": 'No Record'
                    }
            else:
                pengeluaransebenar_list = {
                        "status": 1,
                        "data": pengeluaransebenar_list,

                    }
            return pengeluaransebenar_list
        except Exception as e:
            print(e)

# dashboard list
class getBancianTinggalDashboard_List_ViewDetail(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_bancian_dirian_tinggal_dashboard_viewdetail(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)


# dashboard list
class DashboardSelepasTebangan_List_viewDetail(Resource):
    def get(self,kompatmenid):

        if g.user is None:            
   
            data = {
                "status": 0,
                "data": "Authentication Failed.Kindly login again"
                }            
            
            return data
          
        con, cur = initdb()
        try:

            get_dirian_tinggal= Forest().get_bancianselepastebangan_list_viewdetail(kompatmenid)

            if not get_dirian_tinggal or None:
                get_dirian_tinggal = {
                        "status": 0,
                        "data": 'No Record'
                    }
                return get_dirian_tinggal
            else:
                get_dirian_tinggal = {
                        "status": 1,
                        "data": get_dirian_tinggal,

                    }
                return get_dirian_tinggal
        except Exception as e:
            print(e)






# user management
api.add_resource(Login, '/m/users/login/' )
api.add_resource(UserList, '/m/userlist/')
api.add_resource(Profile, '/m/profile/<userid>')
api.add_resource(DestroySession, '/m/logout/' )
api.add_resource(UpdateUser, '/m/updateuser/<userid>')
api.add_resource(CreateUser, '/m/adduser/')
api.add_resource(DeleteUser, '/m/deleteuser/<userid>')
api.add_resource(getUser, '/m/getuser/')
api.add_resource(ResetPassword, '/m/resetpassword/<userid>')
# productivity management

# GET
api.add_resource(getKompatmen, '/m/getkompatmen/')
api.add_resource(getKompatmenByHutan, '/m/getkompatmenbyhutan/<hutanid>')
api.add_resource(getSite, '/m/getsite/')
api.add_resource(getHutan, '/m/hutanlist/')
api.add_resource(getHutanDetail, '/m/hutandetail/')
api.add_resource(getKerosakan_List, '/m/getkerosakan/')
api.add_resource(getRawatan_List, '/m/getrawatanlist/')
api.add_resource(getTahap_Kerosakan, '/m/gettahapkerosakan/')
api.add_resource(getCheckKoordinate, '/m/getcheckkoordinate/<kompatmenid>')
api.add_resource(PenandaanSempKompartmen, '/m/penandaansempkompatmen/')
api.add_resource(getSempadanList, '/m/sempadanlist/<kompatmenid>')
api.add_resource(getSpesies_Type, '/m/getspesis/')
api.add_resource(getSpesies_Kump, '/m/getkump7/')
api.add_resource(getFamily_Spesies, '/m/getfamilyspesis/')
api.add_resource(getSpesies_List, '/m/getspesisdetail/')
api.add_resource(getBancianTinggal, '/m/getbanciandiriantinggal/<nfctag>')
api.add_resource(Pembalak_getPengeluaranSebenar, '/m/pembalak_getpokokdetail/<nfctag>')
api.add_resource(getKompatmenDetailDashboard, '/m/getkompatmendetail/<kompatmenid>')
api.add_resource(getBancianSelepasTebangan, '/m/getbancianselepastebangan/<nfctag>')
api.add_resource(BancianSebelumTebangan_List, '/m/banciansebelumtebangan_list/<kompatmenid>')
api.add_resource(getBancianTinggalDashboard_List, '/m/getbanciandiriantinggal_dashboard/<kompatmenid>')

api.add_resource(DashboardHadPengeluaranSebenar_List, '/m/hadpengeluaransebenar_list/<kompatmenid>')
api.add_resource(DashboardSelepasTebangan_List, '/m/selepastebangan_list/<kompatmenid>')
api.add_resource(DashboardPokokTebang_List, '/m/pokoktebang_list/<kompatmenid>')
api.add_resource(DashboardPokokTebang_Detail, '/m/pokoktebang_detail/<kompatmenid>')
api.add_resource(Approval_all_list, '/m/approval_all_list/')
api.add_resource(Approval_pending_list, '/m/approval_pending_list/')
api.add_resource(Approval_approve_list, '/m/approval_approve_list/')
api.add_resource(Approval_reject_list, '/m/approval_reject_list/')
api.add_resource(Pegawai_getPengeluaranSebenar, '/m/pegawai_gettualdetail/<nfctag>')
api.add_resource(Pembalak_unread_Notification, '/m/pembalak_unread_notification_list/')
api.add_resource(DashboardPokok_map_dip, '/m/pokok_dip_map/<kompatmenid>')
api.add_resource(DashboardPokok_map_nondip, '/m/pokok_nondip_map/<kompatmenid>')
api.add_resource(Get_Latest_Price_spesies, '/m/get_latest_price_spesies/<spesiesid>')

api.add_resource(DashboardHadPengeluaranSebenar_ViewDetail, '/m/hadpengeluaransebenar_list_viewdetail/<kompatmenid>')
api.add_resource(getBancianTinggalDashboard_List_ViewDetail, '/m/getbanciandiriantinggal_list_viewdetail/<kompatmenid>')
api.add_resource(DashboardSelepasTebangan_List_viewDetail, '/m/selepastebangan_list_viewdetail/<kompatmenid>')




# POST
api.add_resource(CreateFamilySpesis, '/m/familyspesis/')
api.add_resource(CreateKompatmen, '/m/createkompatmen/')
api.add_resource(CreateSubSpesis, '/m/createsubspesies/')
api.add_resource(CreateHutanSimpan, '/m/createhutan/')
api.add_resource(AddRawatan, '/m/addrawatan/')
api.add_resource(BancianSebelumTebangan, '/m/banciansebelumtebangan/')
api.add_resource(PenandaanPokok, '/m/penandaanpokok/')
api.add_resource(Update_PenandaanPokok, '/m/update_penandaanpokok/<nfctag>')
api.add_resource(UpdatePenandaanSempKompartmen, '/m/updatepenandaansempkompatmen/<point_id>')

api.add_resource(PostBancianTinggal, '/m/banciandiriantinggal/<nfctag>')
api.add_resource(Pembalak_Post_Pengeluaran, '/m/pembalak_post_tual_Pengeluaran/<nfctag>')
api.add_resource(Add_Spesies_PriceList, '/m/add_spesiesprice/')
api.add_resource(BancianSelepasTebangan, '/m/bancianselepastebangan/<nfctag>')
api.add_resource(UpdateBancianSebelumTebangan, '/m/updatebanciansebelumtebangan/<pokokid>')
api.add_resource(Add_Tual, '/m/pembalak_addtual/')
api.add_resource(Pegawai_Action_on_Request, '/m/pegawaiaction/<pokokid>')
api.add_resource(Pegawai_Confirm_Tual_price, '/m/pegawaiconfirm_price/<nfctag>')
api.add_resource(Pegawai_Action_on_Final_price, '/m/pegawai_action_price/<nfctag>')
api.add_resource(Pembalak_is_open, '/m/pembalak_is_open_notification/<pokokid>')
api.add_resource(Pembalak_Noti, '/m/notification/')





# if __name__ == '__main__':
#     app.run(debug=True, port=8000)
    



