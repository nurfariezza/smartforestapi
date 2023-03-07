import datetime


def getdict(o):
    dic = {}
    
    if o is None:
        return None
    
    
    return dic

class JsonModel(object):
    
    def tojson(self):
        return getdict(self)

class TLogin(JsonModel):
    
    def __init__(self):
        self.name = None
        self.username = None
        self.password = None


class UserDetail(JsonModel):
    
    def __init__(self):
        self.u_id = 0
        self.username = None
        self.password = None
        self.email = None
        self.roleid = 0
        self.is_approval = 0
        self.cat_id = 0
        self.is_admin =0
        self.contactno = None
        self.status = 0
        self.forgetpass = 0
        self.secretkey =0
        self.group_id = None
        self.created_date = None
        self.createdby = None
        self.role_name = None
        self.access = None
        
    def setfromdic(self, d):
        self.u_id =  d.get('id', 0)
        self.username =  d.get('username', 0)
        self.password =  d.get('password', 0)
        self.email =  d.get('email', 0)
        self.roleid =  d.get('roleid', 0)
        self.is_approval =  d.get('is_approval', 0)
        self.cat_id =  d.get('cat_id', 0)
        self.is_admin =  d.get('is_admin', 0)
        self.contactno =  d.get('contactno', 0)
        self.status =  d.get('status', 0)
        self.forgetpass =  d.get('forgetpass', 0)
        self.secretkey = d.get('secretkey', 0)
        self.group = d.get('group', 0)
        self.created_date = d.get('created_date', 0)
        self.created_by = d.get('created_by', 0)
        self.role_name = d.get('role_name', 0)
        self.access = d.get('access', 0)



class Subsite(JsonModel):
    
    def __init__(self):
        self.id = 0
        self.name = None
        self.state = None
        self.district = None
        self.stateid = 0
        self.type =None
        self.hutan_id =None
        

    def setfromdic(self, d):
        self.id =  d.get('id', 0)
        self.name =  d.get('name', 0)
        self.state =  d.get('state', 0)
        self.district =  d.get('district', 0)
        self.stateid =  d.get('stateid', 0)
        self.type =d.get('type', 0)
        self.hutan_id =d.get('hutan_id', 0)

class Spesies(JsonModel):
    
    def __init__(self):
        self.id = 0
        self.name = None
        self.state = None
        self.district = None
        self.stateid = 0
        self.type =None
        self.hutan_id =None
        

    def setfromdic(self, d):
        self.id =  d.get('id', 0)
        self.name =  d.get('name', 0)
        self.state =  d.get('state', 0)
        self.district =  d.get('district', 0)
        self.stateid =  d.get('stateid', 0)
        self.type =d.get('type', 0)
        self.hutan_id =d.get('hutan_id', 0)

class Kompatmen(JsonModel):
    
    def __init__(self):
        self.id = 0
        self.name = None

    def setfromdic(self, d):
        self.id =  d.get('id', 0)
        self.name =  d.get('name', 0)



class Koordinate(JsonModel):
    
    def __init__(self):
        self.id = 0
        self.HutanSimpan_id = None
        self.kompatmen_id = None
        self.request_date = None
        self.date_created = None

 
    def tojson(self):
        m = super(Koordinate, self).tojson()
        m['date_createdstr'] = self.date_createdstr

        return m


    @property
    def date_createdstr(self):
        s = None
        
        if self.date_created is not None:
            s = self.date_created.strftime('%Y %b %d %H:%M:%S')
            
        return s