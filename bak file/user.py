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

    def get_site(self, email):
        l =[]
        """Get a user by email"""
        con, cur = initdb()
        
        query = """select state.name as state,state.id
                from site_lookup hutan
                left join site_lookup district on hutan.parent_id = district.id
                left join site_lookup state on district.parent_id = state.id
                left join user_site user_site on user_site.site_id = hutan.id  
                left join user user on user.u_id = user_site.user_id
                where user.email=%s  and state.type='state'"""
        data =(email,)
        cur.execute(query,data)
        
        sitelist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        # print(sitelist)
        for r in sitelist:
            o = models.Subsite()
            o.state = r['state']
            o.id= r['id']

            districtlist = self.get_district(o.id,email)
            # o.id = districtlist.stateid
            # print(districtlist)

            l.append(o)

        # 
        if l:
            # print(o.id)
            
            # print(o.id)
            site={

                "state": sitelist,
                # "district": districtlist,

            }


            # return user
            return site
            
        else:
            sitelist = None

        return sitelist


    def get_district(self, siteid,email):
        l =[]
        idx=[]
        """Get a user by email"""
        con, cur = initdb()
        
        query = """select state.id as stateid, district.name as name, district.id as id from 
            site_lookup district 
            left join site_lookup state on district.parent_id = state.id 
            left join user_site user_site on user_site.site_id = state.id 
            left join user user on user.u_id = user_site.user_id 
            where state.id=%s and user.email=%s"""
        data =(siteid,email)
        cur.execute(query,data)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in dlist:
            o = models.Subsite()
            o.id = r['id']
            o.name = r['name']
            idx.append(o.id)
            l.append(o)
          
        if dlist:
            # i=1
            # for i in idx:
            #     # print(i)
            #     # i=int(i)
            #     # hutanlist = self.get_hutan(i,email)
            
            #     dlist.append(hutanlist)
            return dlist
            
        else:
            dlist = None

        return dlist

    def get_hutan(self, hid,email):
        l =[]
        """Get a user by email"""
        con, cur = initdb()
        
        query = """select hutan.name from 
        site_lookup hutan 
       left join site_lookup district on hutan.parent_id = district.id 
       left join site_lookup state on district.parent_id = state.id 
       left join user_site user_site on user_site.site_id = state.id 
       left join user user on user.u_id = user_site.user_id 
        where hutan.parent_id=%s and user.email=%s"""
        # print(hid)
        data =(hid,email)
        cur.execute(query,data)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in dlist:
            o = models.Subsite()
            o.name = r['name']
            l.append(o)

        if l:
            dlist={
                "reserve_forest": dlist
                
            }
            return dlist
            
        else:
            dlist = None

        return dlist



    def logout(self,email):
        email = None
        return dict(message='User Logout')




    def get_by_user_email(self, email):
        b = False
        userid = None
        try:
            con, cur = initdb()
            query = "SELECT u_id FROM  user WHERE email=%s"
            
            data =(email,)
            cur.execute(query,data)
            
            user = cur.fetchone()
            # print(user)
            if user is not None:
                b = True
                userid = user[0]
            
            
        except Exception as e:
            print(e)

        return userid

    def create_user(self, username,password,email, roleid, is_approval,group_id,contactno,siteid):
        try:
            con, cur = initdb()
            validate_uid= self.get_by_user_email(email)
            if validate_uid is None:

                query = "INSERT INTO user (username,password,email, roleid, is_approval,group_id,contactno) values (%s,%s,%s,%s,%s,%s,%s)"
                data =(username,password,email, roleid, is_approval,group_id,contactno)
                # print(data)

                cur.execute(query,data)
                con.commit()
                plist = self.get_parent_site(siteid)
                uid= self.get_by_user_email(email)
                for r in plist:
                    did = r['did']
                    sid = r['sid']
                    self.set_default_site(uid,sid)
                    self.set_default_site(uid,did)
                    self.set_default_site(uid,siteid)




                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Email Already Exist")
       
        except Exception as e:
                print(e)

    def update_user(self, username,password,contactno,roleid, is_approval,group_id,email):
        try:
            con, cur = initdb()
            
            validate_user= self.get_by_user_email(email)
            roleid=group_id
            if validate_user is not None:
                query = "UPDATE user SET username =%s,password =%s, contactno=%s, roleid=%s, is_approval=%s,  group_id=%s  where email=%s"
                data =(username,password,contactno,roleid, is_approval,group_id,email)

                cur.execute(query,data)
                con.commit()

                return dict(status=1, message='Update Successful')
            else:
                 return dict(status=0, message="Failed.No Data Found")
       
        except Exception as e:
                print(e)



    def delete_user(self, email):
        try:
            con, cur = initdb()
            
            validate_user= self.get_by_user_email(email)
            # print(validate_user)
            if validate_user is not None:
                query = "DELETE FROM user where email=%s"
                data =(email,)

                cur.execute(query,data)
                con.commit()

                return dict(status=1, message='Delete Successful')
            else:
                 return dict(status=0, message="Failed.No Data Found")
       
        except Exception as e:
                print(e)



    def penandaan_sempadan(self, kompartment,stesenfrom, stesento, siteid, bearing,jarak,coor_x, coor_y):
        try:
            con, cur = initdb()
            # query = "INSERT INTO user (username,password,email, roleid, is_approval,group_id,contactno) values (%s,%s,%s,%s,%s,%s,%s)"
            # data =(kompartment,stesenfrom, stesento, siteid, bearing,jarak,coor_x, coor_y)

            # cur.execute(query,data)
            # con.commit()
            plist = self.get_parent_site(siteid)
            print(plist)
            # uid= self.get_by_user_email(email)
            for r in plist:
                did = r['did']
                sid = r['sid']
                # self.set_default_site(uid,sid)
                # self.set_default_site(uid,did)
                # self.set_default_site(uid,siteid)
            return dict(message='Successfully Created')
        
        except Exception as e:
                print(e)


    def get_parent_site(self, siteid):
        try:
        
            con, cur = initdb()
            
            
            query = "select district.id as did,district.name as dname,state.id as sid,state.name as sname from site_lookup hutan left join site_lookup district on hutan.parent_id = district.id left join site_lookup state on district.parent_id = state.id where hutan.id = %s"
            data =(siteid,)
            cur.execute(query,data)
            parentsite = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return parentsite
        
        except Exception as e:
                print(e)

    def set_default_site(self, uid,siteid):
        try:
            print(uid, siteid)
            con, cur = initdb()
            query = "INSERT INTO user_site (`site_id`, `user_id`, `default_site`) values (%s,%s,0)"
            data =(siteid,uid)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Created', data=data)
        
        except Exception as e:
                print(e)


# def site_load(hid, email):
#     dic = {}
#     db = None
#     try:
#         db = initdb()
#         dic['state'] = state_get(email, db)
#         dic['district'] = district_list(hid, db)
#         dic['hutan'] = hutan_list(hid, db)
    
#     finally:
#         if db is not None:
#             db.dispose()
            
#     return dic

    # def get_userprofile_email(self, email):
    #     b = False
    #     l=[]
    #     userid = None
    #     print(email)
    #     try:
    #         con, cur = initdb()
    #         query = "SELECT username, email,contactno,group_id, roleid FROM  user WHERE email=%s"
            
    #         data =(email,)
    #         cur.execute(query,data)
            
    #         user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
    #         if user is not None:
                 
    #             return user
           
            
    #     except Exception as e:
    #         print(e)

    #     return userid