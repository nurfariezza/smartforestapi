# import sqlite3
from flask_restful import Resource, reqparse
from dbhelper import initdb
import models, settings
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
from datetime import datetime,timedelta   
from flask import Flask, request,jsonify,session,Response, json
import hashlib
import requests
import smtplib, ssl

class Forest:
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

        query = """SELECT user.u_id,user.email,user.username, user.is_approval, user.contactno, user.is_admin,access_group.group_id, 
        access_group.group,  'access', 'default_reserve_forest' FROM user
         Left Join  access_group
         ON access_group.group_id = user.group_id 
         Left Join user_site 
         ON user.u_id = user_site.user_id 
         left join site_lookup 
         ON user_site.site_id = site_lookup.id
        WHERE user_site.default_site =1 
        and user.email=%s and user.password=%s"""
        data =(email,password)
        cur.execute(query,data)
        
        user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in user:
            o = models.UserDetail()
            o.u_id = r['u_id'] 
            access_role= self.get_access_role(o.u_id)
            r['access']=access_role
            site= self.get_default_site(o.u_id)
            r['default_reserve_forest']=site

        
        if user == []:
            user={
                "status": 0, 
                "data": "User Not Found"
            }
        else:
            user={
                "status": 1, 
                "data": user
            }
        return user

    def get_default_site(self, u_id):
        l =[]
        con, cur = initdb()
        
        query = """select state.name as state, district.name as district, hutan.name as name, hutan.id as hutan_id, 'kompatmen_list'
                from hutan_simpan hutan
                left join site_lookup district on hutan.district = district.id
                left join site_lookup state on district.parent_id = state.id
                left join user_site user_site on user_site.site_id = hutan.id  
                left join user user on user.u_id = user_site.user_id
                where user.u_id=%s and user_site.default_site=1"""
        data =(u_id,)
        cur.execute(query,data)
        
        sitelist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in sitelist:

            hutan_id = r['hutan_id']
            site= self.get_kompatmen_hutanid_profile(hutan_id)
            r['kompatmen_list']=site

        if sitelist:
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
        if not user or None:
            user = {
                    "status": 0,
                    "data": 'Invalid Login'
                }
            return user
        else:

            return user

    def profile(self, userid):
        con, cur = initdb()
        
        query = """SELECT user.u_id,user.email,user.username, user.contactno,user.is_approval, user.is_admin,access_group.group_id, 
        access_group.group,  'access', 'default_reserve_forest' FROM user
         Left Join  access_group
         ON access_group.group_id = user.group_id 
         Left Join user_site 
         ON user.u_id = user_site.user_id 
         left join site_lookup 
         ON user_site.site_id = site_lookup.id
        WHERE user_site.default_site =1 
        and user.u_id=%s """
        data =(userid,)
        cur.execute(query,data)
        
        user = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

        for r in user:
            o = models.UserDetail()
            o.u_id = r['u_id'] 
            o.email = r['email'] 
            access_role= self.get_access_role(o.u_id)
            r['access']=access_role
            site= self.get_default_site(o.u_id)
            r['default_reserve_forest']=site


        if len(user):
            user={
                "status": 1, 
                "data": user
            }
            return user
        else:
            user={
                "status": 0, 
                "data": "User Not Found"
            }

            return user

    def get_access_role(self,uid):
        try:
            con, cur = initdb()
           
            query = "SELECT abu.role_id,ac.role_name FROM access_by_user abu, access_type ac where abu.role_id = ac.role_id and userid=%s"
            data =(uid,)
            cur.execute(query,data)
            access_role = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            # print(access_role)
            return access_role

        except Exception as e:
                print(e)

    def get_site(self):
        l =[]
        con, cur = initdb()
        
        query = """select state.name as state,state.id, 'district' from site_lookup state
         where state.type='state'"""
        # data =(email,)
        cur.execute(query)
        
        sitelist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in sitelist:
            o = models.Subsite()
            o.state = r['state']
            o.id= r['id']
            districtlist = self.get_district(o.id)
            r['district'] =districtlist
            for x in districtlist:
                s = models.Subsite()
                s.id= x['id']
                gethutan = self.get_hutan(s.id)
                x['hutan'] =gethutan



            l.append(o)

        # 
        if l:

            site={
                "state": sitelist,
            }

            return site
            
        else:
            sitelist = None
        return sitelist

    def get_district(self, siteid):
        l =[]
        idx=[]
        con, cur = initdb()
        
        query = """select state.id as stateid, district.name as name, district.id as id,'hutan' from 
            site_lookup district 
            left join site_lookup state on district.parent_id = state.id 
            
            where state.id=%s """

            # and user.email=%s
        data =(siteid,)
        cur.execute(query,data)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in dlist:
            o = models.Subsite()
            o.id = r['id']
            o.name = r['name']
            o.stateid = r['stateid']
            l.append(o)
          
        if dlist:
         
            return dlist
        else:
            dlist = None

        return dlist

    def get_hutan(self, hid):
        l =[]
        con, cur = initdb()
        
        query = """select hutan.id, hutan.name, district.id as districtid from 
            hutan_simpan hutan 
            left join site_lookup district on hutan.district = district.id 
            left join site_lookup state on district.parent_id = state.id 
            where hutan.district=%s"""
        data =(hid,)
        cur.execute(query,data)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in dlist:
            o = models.Subsite()
            o.id = r['id']
            o.name = r['name']
            l.append(o)

        if l:
            
            return dlist
            
        else:
            dlist = None

            return dlist

    def get_hutan_list(self):
        l =[]
        con, cur = initdb()
        
        query = """select hutan.id, hutan.name,hutan.type from 
            hutan_simpan hutan 
            left join site_lookup district on hutan.id = district.id 
            left join site_lookup state on district.parent_id = state.id 
            where hutan.type like '%Hutan Simpan%'"""
        # data =(hid,)
        cur.execute(query)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        for r in dlist:
            o = models.Subsite()
            o.id = r['id']
            o.name = r['name']
            o.type = r['type']
            l.append(o)

        

        return dlist

    def get_hutan_detail(self):
        l =[]
        con, cur = initdb()
        
        query = """select hutan.id, hutan.name,hutan.type,koordinate.dbh,koordinate.bearing, koordinate.jarak, 
        koordinate.kompatmen_id, koordinate.koordinate_x, koordinate.koordinate_y,koordinate.line_from,
        koordinate.line_to, koordinate.spesies, spesies.local_name, spesies.scientific_name from hutan_simpan hutan 
        left join site_lookup district on hutan.id = district.id left join site_lookup state on 
        district.parent_id = state.id left join koordinate koordinate on hutan.id = koordinate.hutansimpan_id 
        left join spesies spesies on koordinate.spesies=spesies.id"""
        # data =(hid,)
        cur.execute(query)
        
        dlist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]     

        return dlist

    def logout(self,email):
        email = None
        return dict(message='User Logout')

    def get_by_user_email(self, email):
        b = False
        userid = None
        try:
            con, cur = initdb()
            query = "SELECT u_id FROM user WHERE email=%s"
            
            data =(email,)
            cur.execute(query,data)
            
            user = cur.fetchone()
            if user is not None:
                b = True
                userid = user[0]
            
            
        except Exception as e:
            print(e)

        return userid

    def get_by_user_u_id(self, u_id):
        b = False
        userid = None
        try:
            con, cur = initdb()
            query = "SELECT u_id FROM user WHERE u_id=%s"
            
            data =(u_id,)
            cur.execute(query,data)
            
            user = cur.fetchone()
            if user is not None:
                b = True
                userid = user[0]
            
            
        except Exception as e:
            print(e)

        return userid

    def create_user(self, username,password,email,is_approval,group_id,is_admin,contactno,siteid,access_role,createdby):
        try:
            con, cur = initdb()
            validate_uid= self.get_by_user_email(email)
            if group_id==1:
                access_role=[1, 2, 3, 4, 5, 6, 7]
                # gg= self.get_access_list()
               
            else:
                access_role = access_role

            if validate_uid is None:

                query = "INSERT INTO user (username,password,email,is_approval,group_id,is_admin,contactno,created_by) values (%s,%s,%s,%s,%s,%s,%s,%s)"
                data =(username,password,email, is_approval,group_id,is_admin,contactno,createdby)

                cur.execute(query,data)
                con.commit()
                plist = self.get_parent_site(siteid)
                uid= self.get_by_user_email(email)
                for r in plist:
                    did = r['did']
                    sid = r['sid']
                    self.set_default_site(uid,sid,0)
                    self.set_default_site(uid,did,0)
                    self.set_default_site(uid,siteid,1)
                    if len(access_role):
                        for role_id in access_role:
                            self.set_accessrole_for_user(role_id,uid)

                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Email Already Exist")
       
        except Exception as e:
                print(e)

    def update_user(self, userid, email,username,contactno,siteid,is_approval,group_id,is_admin,access_role,created_by):

        try:
            con, cur = initdb()
            u_id= self.get_by_user_u_id(userid)
            if group_id==1:
                access_role=[1, 2, 3, 4, 5, 6, 7]
               
            else:
                access_role = access_role
          
            if u_id is not None:
                query = "UPDATE user SET username =%s, contactno=%s, is_approval=%s, group_id=%s, is_admin=%s, created_by=%s where u_id=%s"
                data =(username,contactno,is_approval,group_id,is_admin, created_by,u_id)
                cur.execute(query,data)
                con.commit()

                self.remove_site_for_user(u_id)
                con.commit()

                plist = self.get_parent_site(siteid)
                uid= self.get_by_user_u_id(u_id)
                for r in plist:
                    did = r['did']
                    sid = r['sid']
                    self.set_default_site(uid,sid,0)
                    self.set_default_site(uid,did,0)
                    self.set_default_site(uid,siteid,1)

                    self.remove_accessrole_for_user(u_id)
                    if len(access_role):
                        for role_id in access_role:
                            self.set_accessrole_for_user(role_id,uid)

               
            
                return dict(status=1, message='Update Successful')
            else:
                 return dict(status=0, message="Failed.No Data Found")
       
        except Exception as e:
                print(e)

    def delete_user(self, userid):
        try:
            con, cur = initdb()
            
            u_id= self.get_by_user_u_id(userid)
            # print(validate_user)
            if u_id is not None:
                query = "DELETE FROM user where u_id=%s"
                data =(userid,)

                cur.execute(query,data)
                con.commit()

                query = "DELETE FROM access_by_user where userid=%s"
                data =(u_id,)
                cur.execute(query,data)
                con.commit()

                query = "DELETE FROM user_site where user_id=%s"
                data =(u_id,)
                cur.execute(query,data)
                con.commit()
                return dict(status=1, message='Delete Successful')
            else:
                 return dict(status=0, message="Failed.No Data Found")
       
        except Exception as e:
                print(e)

    def get_parent_site(self, siteid):
        try:
        
            con, cur = initdb()
            
            
            query = "select district.id as did,district.name as dname,state.id as sid,state.name as sname from hutan_simpan hutan left join site_lookup district on hutan.district = district.id left join site_lookup state on district.parent_id = state.id where hutan.id =%s"
            data =(siteid,)
            cur.execute(query,data)
            parentsite = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return parentsite
        
        except Exception as e:
                print(e)

    def set_default_site(self, uid,siteid,default_value):
        try:
            con, cur = initdb()
            query = "INSERT INTO user_site (`site_id`, `user_id`, `default_site`) values (%s,%s,%s)"
            data =(siteid,uid,default_value)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Created', data=data)
        
        except Exception as e:
                print(e)

    def set_accessrole_for_user(self, roleid, user_id):
        try:
            con, cur = initdb()
            query = "INSERT INTO access_by_user (`role_id`, `userid`) values (%s,%s)"
            data =(roleid, user_id)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Created', data=data)
        
        except Exception as e:
                print(e)

    def remove_accessrole_for_user(self, user_id):
        try:
            con, cur = initdb()
            query = "DELETE FROM access_by_user where userid=%s"
            data =(user_id,)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Delete', data=data)
        
        except Exception as e:
                print(e)
    
    def remove_site_for_user(self, user_id):
        try:
            con, cur = initdb()
            query = "DELETE FROM user_site where user_id=%s"
            data =(user_id,)
            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Delete', data=data)
        
        except Exception as e:
                print(e)

    def post_penandaansempkompartmen(self,siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y):
        try:
            con, cur = initdb()
            print(siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y)
            if kompatmen is not None and siteid is not None:
                query = "INSERT INTO koordinate (hutanSimpan_id, kompatmen_id,line_from,line_to, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                data =(siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y)

                cur.execute(query,data)
                con.commit()

                return dict(status=1, message='Successfully Add', data=data)
            else:
                 return dict(status=0, message="Failed.Incomplete Data")
       
        except Exception as e:
                print(e)

    def update_penandaansempkompartmen(self,siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y,point_id):
        try:
            con, cur = initdb()
            print(siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y,point_id)
            if kompatmen is not None and siteid is not None:
                query = """UPDATE koordinate SET hutanSimpan_id=%s, kompatmen_id=%s,line_from=%s,line_to=%s, spesies=%s, dbh=%s,bearing=%s,jarak=%s,koordinate_x=%s,koordinate_y=%s where id=%s"""
                data =(siteid, kompatmen,fromt,pokokstesen, spesies, dbh,bearing,jarak,koordinate_x,koordinate_y,point_id)
                cur.execute(query,data)
                con.commit()

                return dict(status=1, message='Successfully Update', data=data)
            else:
                 return dict(status=0, message="Failed.Incomplete Data")
       
        except Exception as e:
                print(e)

    def create_kompatmen(self,hutan_id, persempadanan_id, keluasan, kelas_hutan, aktiviti_pengurusan_id,name_code):
        try:
            con, cur = initdb()
            validate_data= self.get_kompatmen_name(name_code)

            print(validate_data)
            if validate_data ==[]:

                query = "INSERT INTO kompatmen (hutan_id,persempadanan_id, keluasan, kelas_hutan, aktiviti_pengurusan_id,name_code) values (%s,%s,%s,%s,%s,%s)"
                data =(hutan_id,persempadanan_id, keluasan, kelas_hutan, aktiviti_pengurusan_id,name_code)

                cur.execute(query,data)
                con.commit()


                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Site Already Exist")
       
        except Exception as e:
                print(e)
    
    def get_kompatmen_name(self, name_code):
        try:
            con, cur = initdb()
            if name_code is None:
                query = "select name_code, persempadanan_id, id from kompatmen"
                # data =(name_code,)
                cur.execute(query)
            else:
                query = "select name_code, persempadanan_id, id from kompatmen where name_code = %s"
                data =(name_code,)
                cur.execute(query,data)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return cdetail

        except Exception as e:
                print(e)

    def get_kompatmen_list(self):
        try:
            con, cur = initdb()
         
            query = "select name_code, persempadanan_id, id from kompatmen"
            
            cur.execute(query,)
            klist = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return klist

        except Exception as e:
                print(e)

    def get_kompatmen_byhutan(self, hutanid):
        try:
            con, cur = initdb()
            
            query = """SELECT k.id as kompartment_id, k.persempadanan_id, k.name_code, k.keluasan as keluasan_kompartment, k.kelas_hutan, k.aktiviti_pengurusan_id, hs.id as hutan_id, hs.name as hutan_name, hs.created_date as hutan_created_date, k.created_date as kompartment_created_date FROM kompatmen k 
            left join hutan_simpan hs on hs.id=k.hutan_id
            WHERE k.hutan_id=%s"""
            data =(hutanid,)
            cur.execute(query,data)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(cdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_kompatmen_hutanid_profile(self, hutanid):
        try:
            con, cur = initdb()
            
            query = """SELECT k.id as kompartment_id, k.persempadanan_id, k.name_code, k.keluasan as keluasan_kompartment, k.kelas_hutan FROM kompatmen k 
            
            WHERE k.hutan_id=%s"""
            data =(hutanid,)
            cur.execute(query,data)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(cdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_family_name(self, name):
        try:
            con, cur = initdb()

            query = "SELECT * FROM family_spesies where name =%s"
            data =(name,)
            cur.execute(name,data)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return cdetail

        except Exception as e:
                print(e)

    def get_last_koordinate(self,kompatmenid):
        try:
            con, cur = initdb()
           
            query = "SELECT kompatmen_id,MAX(id) AS id FROM koordinate where kompatmen_id=%s GROUP BY kompatmen_id=%s"
            data =(kompatmenid,kompatmenid)
            cur.execute(query,data)
            id_stesen = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            
            for r in id_stesen:
                id_stesens = r['id']

            # print(id_stesens)
            query = "SELECT line_to as stesen, kompatmen_id FROM koordinate where id=%s and kompatmen_id=%s"
            data =(id_stesens,kompatmenid)
            cur.execute(query,data)
            last_stesen = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            print(last_stesen)
            return last_stesen

        except Exception as e:
                print(e)

    def get_list_sempadan_koordinate(self,kompatmenid):
        try:
            con, cur = initdb()
           
            query = "SELECT koor.*,spes.*, koor.id as point_id FROM koordinate koor, spesies spes where koor.spesies=spes.id and koor.kompatmen_id=%s "
            data =(kompatmenid,)

            cur.execute(query,data)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(cdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_jenis_kerosakan(self):
        try:
            con, cur = initdb()
           
            query = "SELECT j_id, jenis_kerosakan FROM jenis_kerosakan"
            # data =(name_code,)
            cur.execute(query)
            jenis_kerosakan = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return jenis_kerosakan

        except Exception as e:
                print(e)

    def get_jenis_rawatan(self):
        try:
            con, cur = initdb()
            # today = datetime.date.today()
            today = datetime.now()
            year = today.strftime("%Y")

            print(year)
            query = "SELECT id, name, 'year_list' FROM general_lookup where type='jenis_rawatan'"
            # data =(name_code,)
            cur.execute(query)
            jenis_rawatan = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for y in jenis_rawatan:
                y['year_list']= year
                # print(year)
        
            return jenis_rawatan

        except Exception as e:
                print(e)


    def get_tahap_kerosakan(self):
        try:
            con, cur = initdb()
           
            query = "SELECT j_id, jenis_kerosakan FROM level_kerosakan"
            # data =(name_code,)
            cur.execute(query)
            level_kerosakan = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return level_kerosakan

        except Exception as e:
                print(e)

    def get_spesies_type(self):
        try:
            con, cur = initdb()
           
            query = "SELECT id, name,type FROM spesis_lookup where type ='kumpulan_spesis'"
            # data =(name_code,)
            cur.execute(query)
            kumpulan_spesis = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return kumpulan_spesis

        except Exception as e:
                print(e)

    def get_kump_spesies(self):
        try:
            con, cur = initdb()
           
            query = "SELECT id, name,type FROM spesis_lookup where type ='kumpulan_7'"
            cur.execute(query)
            kumpulan_7 = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return kumpulan_7

        except Exception as e:
                print(e)

    def create_familyspesies(self,name,kump_dnd):
        try:
            con, cur = initdb()

            validate_data= self.get_family_name(name)

            if validate_data ==[]:

                query = "INSERT INTO family_spesies (name,kumpulan_d_nd) values (%s,%s)"
                data =(name,kump_dnd)

                cur.execute(query,data)
                con.commit()


                return dict(status=1, message='Family Spesis Created', data=data)
            else:
                 return dict(status=0, message="Failed.Family Spesis Already Exist")
       
        except Exception as e:
                print(e)

    def get_family_spesies(self):
        try:
            con, cur = initdb()
           
            query = "SELECT fs.id as fam_id, fs.name as fam_name,sl.id, sl.name FROM family_spesies fs, spesis_lookup sl where fs.kumpulan_d_nd=sl.id"
            cur.execute(query)
            family_spesies = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return family_spesies

        except Exception as e:
                print(e)

    def create_subspesies(self,family_id,local_name,scientific_name,kumpulan_7):
        try:
            con, cur = initdb()
            if (family_id,local_name,scientific_name) is not None:

                query = "INSERT INTO spesies (family_id,local_name,scientific_name,kumpulan_7) values (%s,%s,%s,%s)"
                data =(family_id,local_name,scientific_name,kumpulan_7)

                cur.execute(query,data)
                con.commit()


                return dict(status=1, message='Spesis Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def getspesies_list(self):
        try:
            con, cur = initdb()
           
            query = """SELECT s.id, s.local_name, s.scientific_name, fs.name as family, fs.kumpulan_d_nd as dip_type, sl.name as type_name,sl7.name as Kump_7_name FROM spesies s 
            Left Join family_spesies fs
            ON fs.id = s.family_id
            Left Join spesis_lookup sl
            ON sl.id = fs.kumpulan_d_nd
            left Join spesis_lookup sl7
            ON sl7.id = s.kumpulan_7"""
            cur.execute(query)
            family_spesies = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
        
            return family_spesies

        except Exception as e:
                print(e)

    def create_hutan(self,state,district,type,name,keluasan,kelas_hutan):
        try:
            con, cur = initdb()
            query = "INSERT INTO hutan_simpan (state,district,type,name,keluasan,kelas_hutan) values (%s,%s,%s,%s,%s,%s)"
            data =(state,district,type,name,keluasan,kelas_hutan)

            cur.execute(query,data)
            con.commit()
            return dict(message='Successfully Created', data=data)
        
        except Exception as e:
                print(e)

    def get_access_list(self):
        l=[]
        try:
            con, cur = initdb()

            query = "SELECT role_id FROM access_type"
            cur.execute(query)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            
            l.append(cdetail)
            return l

        except Exception as e:
                print(e)

    def bancian_pre_tebangan(self,kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual):
        try:
            con, cur = initdb()
            if (kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual) is not None:

                query = "INSERT INTO pre_bancian (kompartmen_id,no_pokok,dbh,spesies,kehadiran_pepanjat,bil_tuai) values (%s,%s,%s,%s,%s,%s)"
                data =(kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual)
                print(data)
                cur.execute(query,data)

                # add pokok detail to pokok table
                self.bancian_pre_tebangan_insert_pokok(kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual)

                self.update_latest_kompatmen_activity(1,kompatment_id)

                self.insert_log_aktiviti(pokok_id=no_pokok, aktiviti_id=1, start_date=None, end_date=None, bil_tual=biltual, isipadu_ha=None, litupan_pepanjat=pepanjat, status_keputusan=None, hidup_mati=None, jenis_kerosakan=None, tahap_kerosakan=None, diameter=None, request_by=None, request_date=None, approve_by=None, approve_date=None, rejected_by=None, rejected_date=None, dbh=dbh, no_petak=None)
                con.commit()

                # send notifcation to pegawai pembalak to inform  proces earlier done

                # headers = {
                # 'Content-type': 'application/json', 'Accept': 'text/plain'
                # }
                
                # URL= 'https://frim.redtone.com/apipy/v1/m/notification/'
                # data1 = {
                # "title": "Proses Bancian Telah Selesai.",
                # "body": "Sila teruskan dengan Penandaan Pokok."
                # }

                # data1= json.dumps(data1)
                # response = requests.post(URL, data=data1, headers=headers)
                # print(response)


                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def update_bancian_pre_tebangan(self,kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual):
        try:
            con, cur = initdb()
            if (kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual) is not None:

                query = """UPDATE pre_bancian SET kompartmen_id=%s,dbh=%s,spesies=%s,kehadiran_pepanjat=%s,bil_tuai=%s where no_pokok=%s
                """
                data =(kompatment_id,dbh,spesies,pepanjat,biltual,no_pokok)
                cur.execute(query,data)

                # update pokok detail to pokok table
                self.update_bancian_pre_tebangan_pokok(kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual)
                con.commit()


                return dict(status=1, message='Successfully Update', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def update_bancian_pre_tebangan_pokok(self,kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual):
        try:
            con, cur = initdb()

            if int(float(dbh)) >=30:
                status_keputusan = 1
            else:
                status_keputusan = 0

            if (kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual) is not None:

                query = """UPDATE pokok SET kompatmen_id=%s,dbh=%s,spesies_id=%s,kehadiran_pepanjat=%s,bil_tual=%s,status_keputusan=%s where no_pokok=%s
                """
                data =(kompatment_id,dbh,spesies,pepanjat,biltual,status_keputusan,no_pokok)
                cur.execute(query,data)
                con.commit()

                return dict(status=1, message='Successfully Created', data=data)
            else:
                return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def bancian_pre_tebangan_insert_pokok(self,kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual):
        try:
            con, cur = initdb()
            if (kompatment_id,no_pokok,dbh,spesies,pepanjat,biltual) is not None:

                query = "INSERT INTO pokok (kompatmen_id,no_pokok,spesies_id,dbh,kehadiran_pepanjat,bil_tual,current_process_id) values (%s,%s,%s,%s,%s,%s,%s)"
                data =(kompatment_id,no_pokok,spesies,dbh,pepanjat,biltual,1)
                cur.execute(query,data)
                con.commit()

       
        except Exception as e:
                print(e)

    def bancian_selepas_tebangan(self,kompatment_id,no_pokok,no_tag,dbh,spesies,pepanjat,biltual):
        try:
            con, cur = initdb()

            if dbh >=30:
                status_keputusan = 1
            else:
                status_keputusan = 0

            if (kompatment_id,no_pokok,no_tag,dbh,spesies,pepanjat,biltual) is not None:

                query = """UPDATE pokok SET kehadiran_pepanjat=%s,bil_tual=%s,dbh=%s,status_keputusan=%s,current_process_id=5 where no_pokok=%s and no_tag=%s
                """
                data = (pepanjat,biltual,dbh,status_keputusan,no_pokok, no_tag)
                cur.execute(query,data)
                con.commit()


                self.insert_log_aktiviti(pokok_id=no_pokok, aktiviti_id=5, start_date=None, end_date=None, bil_tual=biltual, isipadu_ha=None, litupan_pepanjat=pepanjat, status_keputusan=None, hidup_mati=None, jenis_kerosakan=None, tahap_kerosakan=None, diameter=None, request_by=None, request_date=None, approve_by=None, approve_date=None, rejected_by=None, rejected_date=None, dbh=dbh, no_petak=None)
                con.commit()

                self.update_latest_kompatmen_activity(5,kompatment_id)

                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def add_rawatan(self,kompatment_id,jenis_rawatan,tahun):
        try:
            con, cur = initdb()
            if (kompatment_id,jenis_rawatan,tahun) is not None:

                query = "INSERT INTO rawatan_silvikultur (kompartmen_id,jenis_rawatan,tahun) values (%s,%s,%s)"
                data =(kompatment_id,jenis_rawatan,tahun)

                cur.execute(query,data)
                con.commit()

                self.update_latest_kompatmen_activity(6,kompatment_id)

                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def penandaan_pokok(self,kompatmen_id,no_pokok,no_tag,spesies_id,dbh,koordinate_x, koordinate_y,bil_tual):
        try:
            con, cur = initdb()
            # check dbh_value

            if float(dbh) >=30:
                status_keputusan = 1
            else:
                status_keputusan = 0
            
            if (kompatmen_id,no_pokok,no_tag,spesies_id,dbh,bil_tual,koordinate_x, koordinate_y) is not None:
                query = """UPDATE pokok SET no_tag=%s,spesies_id=%s,dbh=%s,koordinate_x=%s, koordinate_y=%s,bil_tual=%s,status_keputusan=%s,current_process_id=3 where no_pokok=%s
                """
                data =(no_tag,spesies_id,dbh,koordinate_x, koordinate_y,bil_tual,status_keputusan,no_pokok)
                cur.execute(query,data)
                con.commit()

                
                bil_tual =int(bil_tual)
                i = 0
                while i < bil_tual:
                    i += 1
                    query = "INSERT INTO tual (no_pokok,no_tual) values (%s,%s)"                    
                    data =(no_pokok,i)
                    
                    cur.execute(query,data)
                    con.commit()
                 
                self.update_latest_kompatmen_activity(3,kompatmen_id)

                # 


                self.insert_log_aktiviti(pokok_id=no_pokok, aktiviti_id=3, start_date=None, end_date=None, bil_tual=bil_tual, isipadu_ha=None, litupan_pepanjat=None, status_keputusan=None, hidup_mati=None, jenis_kerosakan=None, tahap_kerosakan=None, diameter=None, request_by=None, request_date=None, approve_by=None, approve_date=None, rejected_by=None, rejected_date=None, dbh=dbh, no_petak=None)
                con.commit()

                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def update_penandaan_pokok(self,no_tag,kompatmen_id,no_pokok,spesies_id,dbh,koordinate_x, koordinate_y,bil_tual):
        try:
            con, cur = initdb()
            # check dbh_value
            
            if float(dbh) >=30:
                status_keputusan = 1
            else:
                status_keputusan = 0
            
            if (spesies_id,dbh,koordinate_x, koordinate_y,bil_tual,no_pokok,no_tag) is not None:
                query = """UPDATE pokok SET spesies_id=%s,dbh=%s,koordinate_x=%s, koordinate_y=%s,bil_tual=%s,status_keputusan=%s,current_process_id=3 where no_pokok=%s and no_tag=%s
                """
                data =(spesies_id,dbh,koordinate_x, koordinate_y,bil_tual,status_keputusan,no_pokok,no_tag)
               
                print(data)
                cur.execute(query,data)
                con.commit()

                query = """SELECT max(no_tual) as total FROM `tual` WHERE no_pokok=%s"""
                data =(no_pokok,)
                cur.execute(query,data)
                kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
                for k in kdetail:
                    tual_t=k['total']

                # if tual_t==bil_tual:

                # self.insert_log_aktiviti(pokok_id=no_pokok, aktiviti_id=3, start_date=None, end_date=None, bil_tual=bil_tual, isipadu_ha=None, litupan_pepanjat=None, status_keputusan=None, hidup_mati=None, jenis_kerosakan=None, tahap_kerosakan=None, diameter=None, request_by=None, request_date=None, approve_by=None, approve_date=None, rejected_by=None, rejected_date=None, dbh=dbh, no_petak=None)
                # con.commit()
                self.update_latest_kompatmen_activity(3,kompatmen_id)

                return dict(status=1, message='Successfully Update', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def add_bancian_dirian_tinggal(self,no_pokok,pref_id,dbh,status_pokok, jenis_kerosakan,tahap_kerosakan):
        try:
            con, cur = initdb()
            if (no_pokok,pref_id,dbh,status_pokok, jenis_kerosakan,tahap_kerosakan) is not None:

                query = "INSERT INTO stok_dirian_tinggal (pokok_id, pref_id, diameter, status_pokok, jenis_kerosakan, tahap_kerosakan) values (%s,%s,%s,%s,%s,%s)"
                data =(no_pokok,pref_id,dbh,status_pokok, jenis_kerosakan,tahap_kerosakan)

                cur.execute(query,data)
                con.commit()


                query = "select kompatmen_id from pokok where no_pokok=%s"
                cur.execute(query,data)
                kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
                for k in kdetail:
                    kompatment_id = k['kompatmen_id']

                self.update_latest_kompatmen_activity(7,kompatment_id)

                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def get_bancian_dirian_tinggal(self, nfc_tag):
        try:
            con, cur = initdb()
            
            query = """select p.kompatmen_id, p.spesies_id, s.scientific_name,p.no_pokok, p.dbh from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            where p.no_tag=%s"""
         
            data =(nfc_tag,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)

    def get_bancian_dirian_tinggal_dashboard(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select count(p.spesies_id) as bilpokok, p.kompatmen_id, p.spesies_id, s.scientific_name,p.no_pokok, p.dbh from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            where p.kompatmen_id =%s and p.sudah_ditebang=1 group by p.spesies_id"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
          
            return kdetail

        except Exception as e:
                print(e)


    def get_bancian_dirian_tinggal_dashboard_viewdetail(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select p.kompatmen_id, p.spesies_id, s.scientific_name,p.no_pokok, p.koordinate_x, p.koordinate_y,p.dbh, p.kehadiran_pepanjat,p.no_tag, sdt.status_pokok, jk.jenis_kerosakan as jenis_kerosakan, lk.jenis_kerosakan as level_kerosakan, p.updated_date from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            LEFT JOIN stok_dirian_tinggal sdt ON p.no_pokok=sdt.pokok_id
            LEFT JOIN level_kerosakan lk ON sdt.tahap_kerosakan = lk.j_id
            LEFT JOIN jenis_kerosakan jk ON sdt.jenis_kerosakan =jk.j_id
            where p.kompatmen_id =%s and p.sudah_ditebang=1;"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for x in kdetail:
                status_pokok =x['status_pokok']

                if status_pokok == 1:
                    x['status_pokok'] = "Hidup"
                else:
                    x['status_pokok'] = "Mati"
                 
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_kompatmen_detail_dashboard(self, kompatment_id):
        try:
            con, cur = initdb()
            
            # query = """SELECT t.*,r.*,c.name as kelas_hutan_name, d.name FROM general_lookup c, general_lookup d, rawatan_silvikultur r, kompatmen t INNER JOIN ( SELECT kompartmen_id,MAX(id) AS id FROM rawatan_silvikultur GROUP BY kompartmen_id ) tm ON t.name_code = tm.kompartmen_id where r.id = tm.id and t.kelas_hutan = c.id and r.jenis_rawatan=d.id and t.persempadanan_id=%s"""
            query = """SELECT t.*,r.*,c.name as kelas_hutan_name, d.name, la.name as current_act FROM general_lookup c, general_lookup d, rawatan_silvikultur r,lookup_aktiviti la, kompatmen t INNER JOIN ( SELECT kompartmen_id,MAX(id) AS id FROM rawatan_silvikultur GROUP BY kompartmen_id ) tm ON t.name_code = tm.kompartmen_id where r.id = tm.id and t.kelas_hutan = c.id and r.jenis_rawatan=d.id and t.aktiviti_pengurusan_id= la.id and t.persempadanan_id=%s"""
            data =(kompatment_id,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def validate_pokokid(self, pokokid):
        b = False
        try:
            con, cur = initdb()
            query = "SELECT no_pokok FROM `pre_bancian` where no_pokok=%s"
            
            data =(pokokid,)
            cur.execute(query,data)
            
            pokokid = cur.fetchone()
            if pokokid is not None:
                b = True
                pokokid = pokokid[0]
            
            
        except Exception as e:
            print(e)

        return b

    def validate_nfcid(self, nfcid):
        b = False
        try:
            con, cur = initdb()
            query = "SELECT no_tag FROM `pokok` where no_tag=%s"
            
            data =(nfcid,)
            cur.execute(query,data)
            
            nfcid = cur.fetchone()
            if nfcid is not None:
                b = True
                nfcid = nfcid[0]
            
            
        except Exception as e:
            print(e)

        return b

    def validate_is_pokok_exist(self, no_pokok):
        b = False
        try:
            con, cur = initdb()
            query = "SELECT no_pokok FROM `pokok` where no_pokok=%s"
            
            data =(no_pokok,)
            cur.execute(query,data)
            
            no_pokok = cur.fetchone()
            if no_pokok is not None:
                b = True
                no_pokok = no_pokok[0]
            
            
        except Exception as e:
            print(e)

        return b

    def validate_pokokid_stok_dirian_tinggal(self, pokokid):
        b = False
        try:
            con, cur = initdb()
            query = "SELECT pokok_id FROM `stok_dirian_tinggal` where pokok_id=%s"
            
            data =(pokokid,)
            cur.execute(query,data)
            
            pokokid = cur.fetchone()
            if pokokid is not None:
                b = True
                pokokid = pokokid[0]
            
            
        except Exception as e:
            print(e)

        return b

    def get_userlist(self):
        try:
            con, cur = initdb()
            
            query = """SELECT user.u_id,user.created_date, user.email,user.password,user.username, user.is_approval, access_group.group_id, 
            user.is_admin,user.contactno, access_group.group FROM user,  access_group 
            WHERE access_group.group_id = user.group_id 
            """
            cur.execute(query,)
            cdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            # print("here")
            # for k in cdetail:
            #     password=k['password']
            #     password_decr = hashlib.sha256(password.decode('utf-8')).hexdigest()
            #     print(password_decr)
            #     k['password'] = password_decr

            json_str = json.dumps(cdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_pembalak_pengeluaran(self, nfc_tag):
        try:
            con, cur = initdb()
            
            query = """select k.name_code as kompatmen_id, p.bil_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, p.spesies_id, 
            s.scientific_name,p.no_pokok, p.kehadiran_pepanjat,p.dbh, p.koordinate_x, p.koordinate_y, p.isipadu_kasar, p.status_keputusan,p.status_keputusan as bolehditebang, 'tual_detail'
            from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id
            LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id
            LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id
            LEFT JOIN site_lookup sl ON sl.id = hs.district
            LEFT JOIN site_lookup sl2 ON sl2.id=hs.state
            where p.no_tag=%s"""
         
            data =(nfc_tag,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for r in kdetail:
                if r['status_keputusan'] == "1":
                    status_keputusan ="Boleh Ditebang"
                    bolehditebang =True
                else:
                    status_keputusan ="Tidak Boleh Ditebang"
                    bolehditebang =False


                r['status_keputusan']= status_keputusan
                r['bolehditebang']= bolehditebang
                tual_detail=self.get_tual_detail(r['no_pokok'])
                r['tual_detail'] = tual_detail
            return kdetail

        except Exception as e:
                print(e)

    def Pembalak_Post_Tual_PengeluaranSebenar(self,no_pokok,nfc_tag,no_tual,panjang, dbh):
        try:
            con, cur = initdb()
            nfc_validate = self.is_nfc_exist(nfc_tag)
            print(nfc_validate)
            # if nfc_validate is False: 
            #     return dict(status=0, message="Duplicate NFC number")

            if (no_pokok,nfc_tag,no_tual,panjang, dbh) is not None:
                query = "UPDATE tual SET nfcid=%s, panjang_tual=%s, diameter=%s where no_pokok=%s and no_tual=%s"
                data =(nfc_tag,panjang, dbh,no_pokok,no_tual)
                cur.execute(query,data)
                con.commit()

                # update status pokok. Once submit tual value, consider pokok ditebang ooleh pembalak
                query = "UPDATE pokok SET sudah_ditebang =1, current_process_id=4 where sudah_ditebang =0 and no_pokok=%s"
                data =(no_pokok,)
                cur.execute(query,data)
                con.commit()


                #once pembalak tagging nfc, and keyin value, calculate price for each tual 
                tualprice=self.calculate_tual_price(no_pokok,nfc_tag,no_tual,panjang, dbh)
                print(tualprice)

                 # get approval info to send notification\
                pegawai_detail=self.get_pegawai_list()
                for r in pegawai_detail:
                    username = r['username']
                    email = r['email']
                    activity="PS"
                    self.sendmail(username,email,activity)
               
                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def Add_pricelist(self,spesies_id,price,user_id):
        try:
            con, cur = initdb()
            if (spesies_id,price) is not None:

                query = "INSERT INTO spesies_price (spesies_id,price, created_by) values (%s,%s,%s)"
                data =(spesies_id,price,user_id)

                cur.execute(query,data)
                con.commit()


                return dict(status=1, message='Successfully Created', data=data)
            else:
                 return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def is_nfc_exist(self, nfc_tag):
        b = False
        try:
            con, cur = initdb()
            query = "select nfcid from tual where nfcid = %s"
            
            data =(nfc_tag,)
            cur.execute(query,data)
            
            data = cur.fetchone()
            if data is None:
                b = True
        except Exception as e:
            print(e)

        return b
    
    def insert_log_aktiviti(self,pokok_id, aktiviti_id, start_date, end_date, bil_tual, isipadu_ha, litupan_pepanjat, status_keputusan, hidup_mati, jenis_kerosakan, tahap_kerosakan, diameter, request_by, 
            request_date, approve_by, approve_date, rejected_by, rejected_date, dbh, no_petak): 
        con, cur = initdb()

        q = """
            INSERT INTO `log_aktiviti`(`pokok_id`, `aktiviti_id`, `start_date`, `end_date`, `bil_tual`, `isipadu_ha`, `litupan_pepanjat`, `status_keputusan`, `hidup_mati`, `jenis_kerosakan`, `tahap_kerosakan`, `diameter`, `request_by`, 
            `request_date`, `approve_by`, `approve_date`, `rejected_by`, `rejected_date`, `dbh`, `no_petak`) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """
        
        data =(pokok_id, aktiviti_id,start_date, end_date, bil_tual, isipadu_ha, litupan_pepanjat, status_keputusan, hidup_mati, jenis_kerosakan, tahap_kerosakan, diameter, request_by, request_date, approve_by, approve_date, rejected_by, rejected_date, dbh, no_petak)
        cur.execute(q,data)
        con.commit()

    def get_bancian_selepas_tebangan(self, nfc_tag):
        try:
            con, cur = initdb()
            
            query = """select p.kompatmen_id, p.no_tag,p.spesies_id, s.scientific_name,p.no_pokok, p.dbh,p.kehadiran_pepanjat, p.bil_tual from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            where p.no_tag=%s"""
         
            data =(nfc_tag,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)

    def get_bancian_sebelum_tebangan(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select p.kompatmen_id,p.spesies_id, s.scientific_name,p.no_pokok, p.dbh,p.kehadiran_pepanjat, p.bil_tual from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            where p.current_process_id =1 and p.kompatmen_id=%s order by p.id desc"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)

    def get_pengeluaransebenar_list_dashboard(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select count(p.spesies_id) as bilpokok, p.kompatmen_id, p.spesies_id, s.scientific_name,p.no_pokok, p.dbh from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id 
            where p.kompatmen_id =%s and dbh >=30 and sudah_ditebang=0  and current_process_id=3 group by p.spesies_id"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)



    def get_bancianselepastebangan_list_dashboard(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select count(p.spesies_id) as bilpokok, p.kompatmen_id, p.spesies_id, s.scientific_name,
            p.no_pokok, p.dbh,p.updated_date from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id 
            LEFT JOIN stok_dirian_tinggal sdt ON p.no_pokok=sdt.pokok_id where 
            p.kompatmen_id =%s and dbh <=29.9 and current_process_id=5 group by p.spesies_id"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)


    def get_bancianselepastebangan_list_viewdetail(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select  p.kompatmen_id, p.spesies_id, s.scientific_name,p.kehadiran_pepanjat,p.no_tag, p.bil_tual,
            p.no_pokok, p.dbh, p.koordinate_x, p.koordinate_y from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id where 
            p.kompatmen_id =%s and dbh <=29.9 and current_process_id=5"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result       

        except Exception as e:
                print(e)

    def get_senaraipokoktebang_list_dashboard(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select count(p.spesies_id) as bilpokok, p.kompatmen_id, p.spesies_id, s.scientific_name,
            p.no_pokok, p.dbh from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id where 
            p.kompatmen_id =%s and current_process_id=1 group by p.spesies_id"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)

    def get_senaraipokoktebang_detaillist_dashboard(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select  p.kompatmen_id, p.no_tag as penandaan, p.no_tag, p.no_pokok,p.spesies_id, s.scientific_name,
             p.dbh,  p.koordinate_x, p.koordinate_y, p.bil_tual, p.isipadu_kasar from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id where 
            p.kompatmen_id =%s and current_process_id=1 group by p.spesies_id"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for r in kdetail:
                if r['penandaan'] is None:
                    penandaan ="-"
                else:
                    penandaan ="NFC"


                r['penandaan']= penandaan
            return kdetail

        except Exception as e:
                print(e)


    def get_pengeluaransebenar_list_dashboard_viewdetail(self, kompatmenid):
        try:
            con, cur = initdb()
            
            query = """select p.kompatmen_id, p.spesies_id, s.scientific_name,p.no_tag, p.no_pokok, p.koordinate_x, p.koordinate_y, p.dbh,p.updated_date,'tualdetail'
             from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id 
            where p.kompatmen_id =%s and dbh >=30 and sudah_ditebang=0 and current_process_id=3 order by p.updated_date desc"""
            data =(kompatmenid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            for r in kdetail:
            
                no_pokok = r['no_pokok'] 
                pokoklist= self.get_tual_detail_Price(no_pokok)
                r['tualdetail']=pokoklist
                json_str = json.dumps(kdetail)
                result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_tual_detail_Price(self, pokokid):
        try:
            con, cur = initdb()
            
            query = """SELECT id,nfcid,no_pokok,panjang_tual,diameter, harga_cukai,Updated_date FROM `tual`
            where no_pokok=%s """
         
            data =(pokokid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return kdetail

        except Exception as e:
                print(e)


    def get_tual_detail(self, pokokid):
        try:
            con, cur = initdb()
            
            query = """SELECT id,nfcid,no_pokok,panjang_tual,diameter,is_new_tual FROM `tual`
            where no_pokok=%s and status in (0,1,2)"""
         
            data =(pokokid,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]

            return kdetail

        except Exception as e:
                print(e)

    def pembalak_add_tual(self,idxlist,pokok_id,remark,session_user):
        try:
            con, cur = initdb()
            if (idxlist,pokok_id) is not None:
                i = 0
                while i < idxlist:
                    i += 1
                    query = "INSERT INTO tual (no_tual,no_pokok,remark, is_new_tual,request_by,request_date,status) values (%s,%s,%s,%s,%s,%s,%s)"
                    data =(i,pokok_id,remark,1,session_user,datetime.now(),2)

                    cur.execute(query,data)
                    con.commit()


                # get approval info to send notification\
                approver_detail=self.get_approver_list(session_user)
                for r in approver_detail:
                    username = r['username']
                    email = r['email']
                    activity="N"
                    self.sendmail(username,email,activity)

                    # update tual table for approver notification -change to 1
                query = "UPDATE tual SET notify_pegawai=1 where is_new_tual=1 and no_pokok=%s"
                data =(pokok_id,)
                cur.execute(query,data)
                con.commit()
                    #insert notification email info with date,

                
                return dict(status=1, message='Request Submitted', data=data)
            else:
                return dict(status=0, message="Failed.Invalid Data")
       
        except Exception as e:
                print(e)

    def sendmail(self, username,email,activity):
        try:
            # new tual pembalak
            if activity =='N':
                 message = """
                    Salam Sejahtera {0}, <br><br>
                    Notis baru bagi proses permintaan 'Tambah Tual' daripada Pembalak.<br>
                    Untuk maklumat lanjut, <a href="https://frim.redtone.com/">sila klik  pautan ini. </a>
                    E-mel ini dijana secara automatik oleh sistem FRIM. <br>Anda diminta untuk tidak membalas email ini.""".format(username)
                
                #  approvereject
            elif(activity=='AR'):
                 message = """Salam Sejahtera {0}, <br><br>
                    Notis baru. Permintaan anda untuk 'Sahkan Harga' telah diluluskan/ditolak.
                    Untuk maklumat lanjut, <a href="https://frim.redtone.com/">sila klik  pautan ini. </a>
                    E-mel ini dijana secara automatik oleh sistem FRIM.<br> Anda diminta untuk tidak membalas email ini.""".format(username)
                
                #  to be approve
            elif(activity=='TBA'):
                 message = """Salam Sejahtera {0}, <br><br>
                    Notis baru bagi proses 'Sahkan Harga' daripada Pegawai Pengeluar Sebenar.<br>
                    Untuk maklumat lanjut, <a href="https://frim.redtone.com/">sila klik  pautan ini. </a>
                    E-mel ini dijana secara automatik oleh sistem FRIM.<br>Anda diminta untuk tidak membalas email ini.""".format(username)
                 
               #  Pengeluaran Sebenar
            elif(activity=='PS'):
                 message = """Salam Sejahtera {0}, <br><br>
                    Notis baru.Proses Pendaan Tual telah selesai. Sila teruskan dengan proses seterusnya.<br>
                    Untuk maklumat lanjut, <a href="https://frim.redtone.com/">sila klik  pautan ini. </a>
                    E-mel ini dijana secara automatik oleh sistem FRIM.<br>Anda diminta untuk tidak membalas email ini.""".format(username)      
            else:
                message = """Salam Sejahtera {0}, <br><br>
                    Notis baru bagi telah dihantar.<br>
                    Untuk maklumat lanjut, <a href="https://frim.redtone.com/">sila klik  pautan ini. </a>
                    E-mel ini dijana secara automatik oleh sistem FRIM.<br>Anda diminta untuk tidak membalas email ini.""".format(username)
                
            sender_password = settings.password
            session = smtplib.SMTP(settings.smtp_server, settings.port)
            session.login(settings.sender_email, sender_password)
            msg = f'From: {settings.sender}\r\nTo: {email}\r\nContent-Type: text/html; charset="utf-8"\r\nSubject: {settings.theme}\r\n\r\n'
            msg += message
            session.sendmail(settings.sender_email, email, msg.encode('utf8'))
            # session.quit()
        
            return '1: success'

        except Exception as e:
                print(e)

    def get_approver_list(self,session_user):
        try:
            con, cur = initdb()

            query = """SELECT u.u_id,u.group_id,app.username,app.email FROM `user` u left join user app
            ON app.group_id= u.group_id
            where u.u_id=%s and app.is_approval=1"""
         
            data =(session_user,)
            cur.execute(query,data)
            adetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            return adetail

        except Exception as e:
                print(e)


    def get_pegawai_list(self,session_user):
        try:
            con, cur = initdb()

            query = """SELECT u.u_id,u.group_id,app.username,app.email FROM `user` u left join user app
            ON app.group_id= u.group_id
            where u.group_id=4 and app.is_approval=0"""
         
            data =(session_user,)
            cur.execute(query,data)
            adetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            return adetail

        except Exception as e:
                print(e)


    def get_all_list(self):
        try:
            con, cur = initdb()
                
            query = """ 
            select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id LEFT JOIN kompatmen k ON 
            p.kompatmen_id=k.persempadanan_id LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id LEFT JOIN site_lookup sl 
            ON sl.id = hs.district LEFT JOIN site_lookup sl2 ON sl2.id=hs.state RIGHT JOIN tual t ON t.no_pokok=p.no_pokok  LEFT JOIN user u ON u.u_id =t.request_by
            RIGHT JOIN status_lookup ls ON t.status=ls.id where t.notify_pegawai=1 and (t.is_new_tual=1 or t.is_pengeluaran=1) and t.status=2 GROUP BY p.no_pokok

            UNION ALL
            select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid  from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id 
            LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id 
            LEFT JOIN site_lookup sl ON sl.id = hs.district LEFT JOIN site_lookup sl2 ON sl2.id=hs.state 
            RIGHT JOIN tual t ON t.no_pokok=p.no_pokok LEFT JOIN user u ON u.u_id =t.request_by 
            RIGHT JOIN status_lookup ls ON t.status=ls.id where t.status=1 GROUP BY p.no_pokok

            
            UNION ALL
            select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid 
            from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id 
            LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id LEFT JOIN site_lookup sl ON sl.id = hs.district LEFT JOIN site_lookup sl2 
            ON sl2.id=hs.state RIGHT JOIN tual t ON t.no_pokok=p.no_pokok LEFT JOIN user u ON u.u_id =t.request_by 
            RIGHT JOIN status_lookup ls ON t.status=ls.id where  t.status=3 GROUP BY p.no_pokok
            """

            cur.execute(query,)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for k in kdetail:
                aktiviti= k['is_new_tual']
                t_tual = int(k['tual_tambahan'])+int(k['tual_lama'])
                if aktiviti ==1:
                    aktiviti_name ='Penuaian (Tambahan Tual)'
                    k['total_tual']=t_tual
                else:
                    aktiviti_name ='Pengeluaran Sebenar'
                    k['total_tual']=k['tual_lama']

                k['aktiviti_name'] = aktiviti_name           
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_pending_list(self):
        try:
            con, cur = initdb()
            
            query = """select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id LEFT JOIN kompatmen k ON 
            p.kompatmen_id=k.persempadanan_id LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id LEFT JOIN site_lookup sl 
            ON sl.id = hs.district LEFT JOIN site_lookup sl2 ON sl2.id=hs.state RIGHT JOIN tual t ON t.no_pokok=p.no_pokok  LEFT JOIN user u ON u.u_id =t.request_by
            RIGHT JOIN status_lookup ls ON t.status=ls.id where t.notify_pegawai=1 and (t.is_new_tual=1 or t.is_pengeluaran=1) and t.status=2 GROUP BY p.no_pokok"""
        
            cur.execute(query,)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for k in kdetail:
                aktiviti= k['is_new_tual']
                t_tual = int(k['tual_tambahan'])+int(k['tual_lama'])


                if aktiviti ==1:
                    aktiviti_name ='Penuaian (Tambahan Tual)'
                    k['total_tual']=t_tual

                else:
                    aktiviti_name ='Pengeluaran Sebenar'
                    k['total_tual']=k['tual_lama']

                k['aktiviti_name'] = aktiviti_name
            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_approved_list(self):
        try:
            con, cur = initdb()
            
            query = """select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid  from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id 
            LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id 
            LEFT JOIN site_lookup sl ON sl.id = hs.district LEFT JOIN site_lookup sl2 ON sl2.id=hs.state 
            RIGHT JOIN tual t ON t.no_pokok=p.no_pokok LEFT JOIN user u ON u.u_id =t.request_by 
            RIGHT JOIN status_lookup ls ON t.status=ls.id where t.status=1 GROUP BY p.no_pokok"""
        
            cur.execute(query,)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for k in kdetail:
                aktiviti= k['is_new_tual']
                t_tual = int(k['tual_tambahan'])+int(k['tual_lama'])

                if aktiviti ==1:
                    aktiviti_name ='Penuaian (Tambahan Tual)'
                    k['total_tual']=t_tual

                else:
                    aktiviti_name ='Pengeluaran Sebenar'
                    k['total_tual']=k['tual_lama']

                k['aktiviti_name'] = aktiviti_name

            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_reject_list(self):
        try:
            con, cur = initdb()
            
            query = """select bil_tual as tual_lama, count(t.is_new_tual) as tual_tambahan, p.kompatmen_id, p.kehadiran_pepanjat, p.bil_tual, t.panjang_tual, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, 
            p.spesies_id, s.scientific_name,p.no_pokok, p.dbh, p.status_keputusan, t.notify_pegawai, t.remark, u.username as request_by, t.request_date,
            t.status,ls.name,'aktiviti_name', t.is_new_tual, t.is_pengeluaran, 'total_tual',t.id as tual_id, t.harga_cukai,t.nfcid 
            from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id 
            LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id LEFT JOIN site_lookup sl ON sl.id = hs.district LEFT JOIN site_lookup sl2 
            ON sl2.id=hs.state RIGHT JOIN tual t ON t.no_pokok=p.no_pokok LEFT JOIN user u ON u.u_id =t.request_by 
            RIGHT JOIN status_lookup ls ON t.status=ls.id where  t.status=3 GROUP BY p.no_pokok"""
        
            cur.execute(query,)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for k in kdetail:
                aktiviti= k['is_new_tual']
                t_tual = int(k['tual_tambahan'])+int(k['tual_lama'])

                if aktiviti ==1:
                    aktiviti_name ='Penuaian (Tambahan Tual)'
                    k['total_tual']=t_tual

                else:
                    aktiviti_name ='Pengeluaran Sebenar'
                    k['total_tual']=k['tual_lama']

                k['aktiviti_name'] = aktiviti_name

            json_str = json.dumps(kdetail)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def pegawai_approve_add_tual_request(self, pokok_id,tual_asal,tual_tambahan,status,session_user):
        try:
            print(status)
            print(type(status))
            total_tual= int(tual_asal)+int(tual_tambahan)
            con, cur = initdb()
            # if status == 1:
            query = "UPDATE tual SET notify_pegawai=0, notify_pembalak=1, is_new_tual=0, status=%s, approve_by=%s, approve_date=%s where is_new_tual=1 and no_pokok=%s"
            data =(status,session_user,datetime.now(),pokok_id)
            print(data)
            cur.execute(query,data)
            con.commit()

            if status == 1:
                query = "UPDATE pokok SET bil_tual=%s where no_pokok=%s"
                data =(total_tual,pokok_id)
                print(data)
                cur.execute(query,data)
                con.commit()

            if status==1:
                status_val='DiLuluskan'
            else:
                 
                status_val='Ditolak'
            # send notifcation to pegawai pembalak to inform  proces earlier done
                   
            headers = {
            'Content-type': 'application/json', 'Accept': 'text/plain'
            }
            URL= 'https://frim.redtone.com/apipy/v1/m/notification/'
            data1 = {
            "title": "Permohonan Tambah Tual Telah {0}.".format(status_val),
            "body": "Sila teruskan dengan Penandaan Tual."
            }

            data1= json.dumps(data1)
            response = requests.post(URL, data=data1, headers=headers)
            print(response)
                
            return dict(status=1, message='Data Submitted', data=data)
           

        except Exception as e:
                print(e)

    def calculate_tual_price(self, no_pokok,nfc_tag,no_tual,panjang, dbh):
        try:

            # no_pokok,nfc_tag,no_tual,panjang, dbh
            con, cur = initdb()
            
            query = """select p.kompatmen_id, p.spesies_id, s.scientific_name,
            p.no_pokok, p.dbh,sp.price, sp.id as price_id from pokok p LEFT JOIN spesies s ON s.id=p.spesies_id 
            LEFT JOIN spesies_price sp ON p.spesies_id=sp.spesies_id  
            where p.no_pokok=%s"""
         
            data =(no_pokok,)
            cur.execute(query,data)
            pricedetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            for r in pricedetail:
                price_id = r["price_id"]
                spesies_price = r["price"]
                kompatmen_id = r["kompatmen_id"]

            calc_tual_price= float(dbh)*float(spesies_price)
            act_price_convert=f"{calc_tual_price: .2f}"

            query = """UPDATE tual SET harga_cukai=%s, cukai_price_id=%s, final_date_cukai=%s, nfcid=%s, is_pengeluaran =%s where no_pokok=%s and no_tual=%s"""
            data =(act_price_convert,price_id, datetime.now(),nfc_tag, 1,no_pokok,no_tual)
            cur.execute(query,data)
            con.commit()

            self.update_latest_kompatmen_activity(8,kompatmen_id)
            return pricedetail

        except Exception as e:
                print(e)

    def get_pegawai_pengeluaranSebenar_cukai(self, nfc_tag):
        try:
            con, cur = initdb()
            
            query = """select k.name_code as kompatmen_id, sl2.name as state,sl.name as district,k.hutan_id,hs.name as hutan_name, p.spesies_id, 
            s.scientific_name,p.no_pokok, p.dbh as dbh_pokok, p.koordinate_x, p.koordinate_y,t.no_tual, t.panjang_tual, t.diameter, t.harga_cukai,t.cukai_price_id
            from pokok p 
            LEFT JOIN spesies s ON  s.id=p.spesies_id
            LEFT JOIN kompatmen k ON p.kompatmen_id=k.persempadanan_id
            LEFT JOIN hutan_simpan hs ON hs.id=k.hutan_id
            LEFT JOIN site_lookup sl ON sl.id = hs.district
            LEFT JOIN site_lookup sl2 ON sl2.id=hs.state
            LEFT JOIN tual t ON  p.no_pokok=t.no_pokok
            where t.nfcid=%s"""
         
            data =(nfc_tag,)
            cur.execute(query,data)
            kdetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]
            # for r in kdetail:

            return kdetail

        except Exception as e:
                print(e)

    def pegawai_confirm_tual_price(self, nfctag,pokok_id,spesies_id,diameter,price_id,tual_price,session_user):
          
        try:

            con, cur = initdb()


            query = """UPDATE tual SET notify_pegawai=1, status=2, cukai_price_id=%s,harga_cukai=%s,request_by=%s where no_pokok=%s and nfcid=%s"""
            data =(price_id,tual_price,session_user,pokok_id,nfctag)
            print(data)
            cur.execute(query,data)
            con.commit()

            query = """UPDATE pokok SET spesies_id=%s where no_pokok=%s"""
            data =(spesies_id,pokok_id)
            # print(data)
            cur.execute(query,data)
            con.commit()

            # get approval info to send notification\
            approver_detail=self.get_approver_list(session_user)
            for r in approver_detail:
                username = r['username']
                email = r['email']
                activity="TBA"
                self.sendmail(username,email,activity)
            
            return dict(status=1, message='Data Submitted', data=data)
           

        except Exception as e:
                print(e)

    def pegawai_approve_reject_price(self, nfctag,pokok_id,tual_price,status,session_user):
          
        try:

            con, cur = initdb()
            query = """UPDATE tual SET notify_pegawai=0, status=%s, harga_cukai=%s,request_by=%s where no_pokok=%s and nfcid=%s"""
            data =(status,tual_price,session_user,pokok_id,nfctag)
            print(data)
            cur.execute(query,data)
            con.commit()

            # send notification to the pengeluaran group
            group_email=self.get_group_list(session_user)
            for r in group_email:
                username = r['username']
                email = r['email']
                activity="AR"
                self.sendmail(username,email,activity)
            
            return dict(status=1, message='Data Submitted', data=data)
           

        except Exception as e:
                print(e)

    def get_group_list(self,session_user):
        try:
            con, cur = initdb()

            query = """SELECT u.u_id,u.group_id,app.username,app.email FROM `user` u left join user app
            ON app.group_id= u.group_id
            where u.u_id=%s and app.is_approval=0"""
         
            data =(session_user,)
            cur.execute(query,data)
            adetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            return adetail

        except Exception as e:
                print(e)

    def pembalak_is_open_noti(self,pokok_id,bil_tual,status,session_user):
        try:
            con, cur = initdb()
            if (pokok_id,status) is not None:
            # update tual table for approver notification -change to 1
                query = "UPDATE tual SET is_open=%s, no_tual=%s where notify_pembalak=1 and no_pokok=%s"
                data =(status,bil_tual,pokok_id)
                cur.execute(query,data)
                con.commit()
                    #insert notification email info with date,

                
                return dict(status=1, message='Request Submitted', data=data)
            else:
                return dict(status=0, message="Failed.Invalid Data")
        
        except Exception as e:
                print(e)

    def pembalak_unread_notification_list(self):
        try:
            con, cur = initdb()

            query = """SELECT no_pokok,request_date FROM `tual`
            where notify_pegawai=1 and is_open= 0 group by no_pokok"""
         
            # data =(session_user,)
            cur.execute(query,)
            noti = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            json_str = json.dumps(noti)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def pokok_list_NonDip(self,kompatmenid):
        try:
            con, cur = initdb()

            query = """SELECT fs.kumpulan_d_nd as dip_type,p.kompatmen_id,s.scientific_name,p.no_pokok, p.no_tag,p.koordinate_x, p.koordinate_y  FROM spesies s 
            Left Join family_spesies fs
            ON fs.id = s.family_id
            Left Join spesis_lookup sl
            ON sl.id = fs.kumpulan_d_nd
            left Join spesis_lookup sl7
            ON sl7.id = s.kumpulan_7
            Left join pokok p 
            ON p.spesies_id= s.id
            where p.kompatmen_id=%s and p.no_tag is not null and fs.kumpulan_d_nd=2 order by p.id desc"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            noti = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            json_str = json.dumps(noti)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)
    

    def pokok_list_Dip(self,kompatmenid):
        try:
            con, cur = initdb()

            query = """SELECT fs.kumpulan_d_nd as dip_type,p.kompatmen_id,s.scientific_name,p.no_pokok, p.no_tag,p.koordinate_x, p.koordinate_y  FROM spesies s 
            Left Join family_spesies fs
            ON fs.id = s.family_id
            Left Join spesis_lookup sl
            ON sl.id = fs.kumpulan_d_nd
            left Join spesis_lookup sl7
            ON sl7.id = s.kumpulan_7
            Left join pokok p 
            ON p.spesies_id= s.id
            where p.kompatmen_id=%s and p.no_tag is not null and fs.kumpulan_d_nd=1 order by p.id desc"""
         
            data =(kompatmenid,)
            cur.execute(query,data)
            noti = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            json_str = json.dumps(noti)
            result = json.loads(json_str)
            return result

        except Exception as e:
                print(e)

    def get_latest_price_byspesies(self,spesiesid):

        try:
            con, cur = initdb()

            query = """select max(sp.price) as price, max(sp.id) as price_id, s.scientific_name,sp.id from spesies s LEFT JOIN spesies_price sp ON s.id=sp.spesies_id where sp.spesies_id=%s"""
         
            data =(spesiesid,)
            cur.execute(query,data)
            adetail = [dict((cur.description[i][0], value) for i, value in enumerate(row)) for row in cur.fetchall()]


            return adetail

        except Exception as e:
                print(e)

    def reset_password(self, userid, email,password,created_by):

        try:

            con, cur = initdb()
          
            if password is not None or email is not None:
                query = "UPDATE user SET password =%s where u_id=%s"
                data =(password,userid)
                cur.execute(query,data)
                con.commit()

            
                return dict(status=1, message='Reset Successful')
            else:
                 return dict(status=0, message="Failed.No Data Found")
       
        except Exception as e:
                print(e)

    def update_latest_kompatmen_activity(self,activity_id,kompatment_id):
        try:
            con, cur = initdb()

            if (activity_id,kompatment_id) is not None:

                query = """UPDATE kompatmen SET aktiviti_pengurusan_id =%s , updated_date=%s WHERE name_code = %s
                """
                data =(activity_id,datetime.now(),kompatment_id)
                cur.execute(query,data)
                con.commit()
       
        except Exception as e:
                print(e)

