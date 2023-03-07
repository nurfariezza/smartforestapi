from flask import Flask, request,jsonify
from flask_restful import Resource, Api
from dbhelper import initdb
from models import TLogin
import mysql.connector,json
import models
# from resource import resourceapi

from flask_httpauth import HTTPBasicAuth


auth = HTTPBasicAuth()


@auth.verify_password
def verify(username, password):
    l = []
    con, cur = initdb()
    try:
        q = """
            select name, password from user where name =%s and password=%s             
            """
        data = (username,password)
        cur.execute(q,data)
        res = cur.fetchall()
        for r in res:
            o = models.TLogin()
            o.name=r[0]
            o.password=r[1]
            l.append(o)

            

        if (username == o.name and  password==password):
            return True
        else:
            return "Authentication Failed"
        # if not(username and password):
        #     return False
        # return l.get(o.name) == password

    except Exception as e:
            print(e)


class  TotalDevice(Resource):
    @auth.login_required

    def get(self,routerid):
        # l=[]
        con, cur = initdb()
        try:
            q = """
                select count(*) as 'Total Sensor', routerid from routerinfo where routerid =%s            
                """
            data = (routerid,)
            cur.execute(q,data)
            res = cur.fetchall()
            # print(res)
            data_json = []

            columnNames = [column[0] for column in cur.description]

            for rows in res:
                data_json.append( dict( zip( columnNames , rows ) ) )

        
        except Exception as e:
            print(e)
        
        # if jsonify(data_json) == l:
        #     return jsonify({'message': 'Record not found'})
        # else:

        # return jsonify({'message': 'Record not found'})
        return jsonify(data_json)



class  RouterInfo(Resource):
    @auth.login_required

    def get(self,routerid):
        con, cur = initdb()
        try:
            q = """
                select * from routerinfo where routerid =%s            
                """
            data = (routerid,)
            cur.execute(q,data)
            res = cur.fetchall()
            # print(res)
            data_json = []

            columnNames = [column[0] for column in cur.description]

            for rows in res:
                data_json.append( dict( zip( columnNames , rows ) ) )

        
        except Exception as e:
            print(e)
    

        # return jsonify({'message': 'Record not found'})
        return jsonify(data_json)




class  SensorTotal(Resource):
    # @jwt_required()
    @auth.login_required
    def get(self):
        con, cur = initdb()
        try:
            q = """
                SELECT count(*) as 'Total Sensor' FROM `routerinfo`             
                """

                #  select * from data a, routerinfo b where a.routerid =b.routerid 
            cur.execute(q)
            res = cur.fetchall()
            print(res)
            data_json = []

            columnNames = [column[0] for column in cur.description]

            for rows in res:
                data_json.append( dict( zip( columnNames , rows ) ) )

        
        except Exception as e:
            print(e)
    

        # return jsonify({'message': 'Record not found'})
        return jsonify(data_json)


class  DeviceInfo(Resource):
    # @jwt_required()
    @auth.login_required
    def get(self,deviceid):
        con, cur = initdb()
        print(deviceid)
        data_json = []
        try:
            q = """
                select * FROM durian.device where deviceid = %s
                """

            data = (deviceid,)
            # print(q)
            cur.execute(q, data)
            res = cur.fetchall()
            # print(res)
            columnNames = [column[0] for column in cur.description]

            for rows in res:
                data_json.append( dict( zip( columnNames , rows ) ) )

        except Exception as e:
            print(e)
        return jsonify(data_json)
    # def post(self, name):


    # def post(self, name):
    #     if next(filter(lambda x: x['name'] == name, items), None):
    #         return {'message': "An item with name '{}' already exixts.".format(name)}, 400

    #     data =  request.get_json()
    #     item = {'name': name, 'price': data['price']}
    #     items.append(item)
    #     return item,201

    # def delete(self, name):
    #     global items
    #     items = list(filter(lambda x: x['name'] !=name, items))
    #     return {'message': 'Item Deleted'}
    

    # def put(self, name):
    #     global items
    #     item = next(filter(lambda x: x['name'] !=name, items), None)
    #     if item is None:
    #         item ={'name':name, 'price' :data['price']}
    #         items.append(item)
    #     else:
    #         item.update(data)
    #     return item


    

# userlist by routerid
class UserList(Resource):
    def __init__(self):
        pass
        
    @auth.login_required

    def get(self,userid):
        con, cur = initdb()
        try:
            q = """
                select * from user where userid =%s
            
                """
            data = (userid,)
            cur.execute(q, data)
            res = cur.fetchall()
            # print(res)
            data_json = []

            columnNames = [column[0] for column in cur.description]

            for rows in res:
                data_json.append( dict( zip( columnNames , rows ) ) )

                # if not len(data_json)== False:
                # return jsonify(data_json)

        except Exception as e:
            print(e)
 

        return jsonify(data_json)