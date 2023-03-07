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
        self.group = None
        self.created_date = None
        self.createdby = None
        self.role_name = None
        
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


class Subsite(JsonModel):
    
    def __init__(self):
        self.id = 0
        self.name = None
        self.state = None
        self.daerah = None
        self.hutansimpan = None


    def setfromdic(self, d):
        self.id =  d.get('id', 0)
        self.name =  d.get('name', 0)
        self.state =  d.get('state', 0)
        self.daerah =  d.get('daerah', 0)
        self.hutansimpan =  d.get('hutansimpan', 0)



        
   
