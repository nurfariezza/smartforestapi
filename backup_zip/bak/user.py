# import sqlite3
from flask_restful import Resource, reqparse
from dbhelper import initdb
import models
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from datetime import datetime,timedelta   
from flask import Flask, request,jsonify,session,Response, json

class User:
    """User Model"""
    def __init__(self):
        return

    def get_all(self):
        """Get all users"""
        con, cur = initdb()
        query = "SELECT * FROM user "
        cur.execute(query)
        
        users = cur.fetchall()
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_by_id(self, user_id):
        """Get a user by id"""
        con, cur = initdb()
        print("1")

        print(user_id)
        query = "SELECT * FROM user WHERE id=%s"
        data =(user_id,)
        cur.execute(query,(data))
        
        user = cur.fetchone()
        if not user:
            return
        user["_id"] = str(user["_id"])
        user.pop("password")
        return user



    def get_by_email(self, email, password):
        """Get a user by email"""
        l =[]
        con, cur = initdb()
        
        query = "SELECT user.email,user.username, user.is_approval, user_cate.group_id, user_cate.group, role.role_id, role.role_name FROM user, user_site, role, user_cate, site_lookup WHERE role.role_id =user.roleid and user_cate.group_id = user.group_id and user.u_id = user_site.user_id and user_site.site_id = site_lookup.id and user_site.default_site =1 and user.email=%s and user.password=%s "
        data =(email,password)
        cur.execute(query,data)
        
        user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        print(user)

        if user is not None:
            site= self.get_default_site(email)


            user={
                "status": 1, 
                "data": user,
                "default_reserve_forest": site
            }


            return user
            
        else:
            user = None

            return user


    def get_default_site(self, email):
        l =[]
        """Get a user by email"""
        con, cur = initdb()
        
        query = """select state.name as state, district.name as district, hutan.name as name
                from site_lookup hutan
                left join site_lookup district on hutan.parent_id = district.id
                left join site_lookup state on district.parent_id = state.id
                left join user_site user_site on user_site.site_id = hutan.id  
                left join user user on user.u_id = user_site.user_id
                where user.email=%s and user_site.default_site=1"""
        data =(email,)
        cur.execute(query,data)
        
        sitelist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        # print(sitelist)
        for r in sitelist:
            o = models.Subsite()
            o.state = r['state']
            o.district = r['district']
            o.name = r['name']
            l.append(o)

        if l:
            return sitelist
            
        else:
            sitelist = None

        return sitelist

    def encrypt_password(self, password):
        """Encrypt password"""
        return generate_password_hash(password)

    def login(self, email, password):
        """Login a user"""
        user = self.get_by_email(email, password)
        # print(user)
        if not user or None:
            user = {
                    "status": 0,
                    "data": 'Invalid Login'
                }
            return user
        else:

            return user

    def profile(self, email):
        con, cur = initdb()
        
        query = "SELECT user.email,user.username, user.is_approval, user_cate.group_id, user_cate.group, role.role_id, role.role_name FROM user, user_site, role, user_cate, site_lookup WHERE role.role_id =user.roleid and user_cate.group_id = user.group_id and user.u_id = user_site.user_id and user_site.site_id = site_lookup.id and user_site.default_site =1 and user.email=%s "
        data =(email,)
        cur.execute(query,data)
        
        user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        # print(user)

        if user is not None:
            site= self.get_default_site(email)

            user={
                "status": 1, 
                "data": user,
                "default_reserve_forest": site
            }


            return user
            
        else:
            user = None

            return user

    

    def logout(self,email):
        email = None
        return dict(message='User Logout')




    def get_by_user_email(self, email):
        b = False
        userid = None
        try:
            con, cur = initdb()
            query = "SELECT userid FROM  user WHERE email=%s"
            
            data =(email,)
            cur.execute(query,data)
            
            user = cur.fetchone()
            # print(user)
            if user is not None:
                b = True
                userid = user.userid
            
            
        except Exception as e:
            print("3")
            print(e)

        return userid

    def add_newuser(self, username, email, roleid,password,contactno, is_approval,group_id):
        try:
            con, cur = initdb()
            query = "INSERT INTO  user (username,email, roleid,password, contactno, is_approval, group_id) values (%s,%s,%s,%s,%s,%s,%s)"
            data =(username, email, roleid,password,contactno, is_approval,group_id)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Created', data=data)
        
        except Exception as e:
                print(e)
        


