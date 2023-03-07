# coding=utf-8
import json, random
# from . import constants
# from django.http.response import HttpResponse
# from dbhelper import DbHelper

# def connectGWDB(igatetype, autocommit=True):
#     db = None
#     gw = ''

#     try:
#         if igatetype == constants.GWID.GWAM:
#             gw = 'AM'
#             db = DbHelper('192.168.128.1,2234', 'NewIddGateway', 'GoldenKey', 'GoldenKey')
#             db.connect(autocommit=autocommit)

#         elif igatetype == constants.GWID.GWCP:
#             raise UIException('CP gateway does not have direct connection')

#         elif igatetype == constants.GWID.GWKLP:
#             gw = 'KP'
#             db = DbHelper('192.168.128.1,3235', 'NewIddGateway', 'PaymentTopup', 'redtonePaymentTopup')
#             db.connect(autocommit=autocommit)

#         elif igatetype == constants.GWID.GWPD:
#             gw = 'PD'
#             db = DbHelper('192.168.128.1,1234', 'NewIddGateway', 'sa', 'RedTone')
#             db.connect(autocommit=autocommit)

#         elif igatetype == constants.GWID.GWSB:
#             gw = 'SB'
#             db = DbHelper('192.228.118.135,6004', 'NewIddGateway', 'PaymentTopup', 'redtonePaymentTopup')
#             db.connect(autocommit=autocommit)

#         elif igatetype == constants.GWID.GWPDDB2:
#             gw = 'PDDB2'
#             db = DbHelper('192.168.128.1,1235', 'NewIddGateway', 'GoldenKey', 'GoldenKey')
#             db.connect(autocommit=autocommit)

#     except UIException:
#         db = None
#         raise

#     except Exception:
#         db = None
#         raise UIException('Failed to connect to {0} gateway'.format(gw))

#     return db, gw

# def connectRTSMSDB(autocommit=True):
#     db = None

#     try:
#         login, pwd = getdatabaseloginpassword('RTSMS')
#         db = DbHelper('192.168.1.51', 'RTSMS', login, pwd)
#         db.connect(autocommit=autocommit)

#     except UIException:
#         db = None
#         raise

#     except Exception:
#         db = None
#         raise

#     return db

# def connectAMDB1(autocommit=True):
#     db = None

#     try:
#         login, pwd = getdatabaseloginpassword('GoldenKey')
#         db = DbHelper('192.168.128.1,2234', 'NewIddGateway', login, pwd)
#         db.connect(autocommit=autocommit)

#     except UIException:
#         db = None
#         raise

#     except Exception:
#         db = None
#         raise

#     return db

# def connectAMDB1WebCentric(autocommit=True):
#     db = None

#     try:
#         db = DbHelper('192.168.1.51', 'WebCentric', 'wingfei.siew', 'wingfei.siew')
#         db.connect(autocommit=autocommit)

#     except Exception:
#         db = None
#         raise

#     return db


# def connectMetaSwitchCDR(autocommit=True):
#     db = None

#     try:
#         #db = DbHelper('192.168.138.172', 'NewIddGateway', 'wingfei', 'wingfei')

#         db = DbHelper('192.168.138.120', 'MetaSwitchCDR', 'CallBilling', 'CBPWD12345')
#         db.connect(autocommit=autocommit)

#     except Exception:
#         db = None
#         raise

#     return db

# def getdatabaseloginpassword(appname, loginid=None):
#     db = None
#     q = None
#     login = None
#     pwd = None

#     try:
#         db = DbHelper()
#         db.connect()

#         if loginid is not None:
#             q = """
#                 select applicationname, loginid, password, newpassword from ApplicationDBLogin
#                 where applicationname = ? and loginid = ?
#                 """
#             db.cur.execute(q, appname, loginid)

#         else:
#             q = """
#                 select applicationname, loginid, password, newpassword from ApplicationDBLogin
#                 where applicationname = ?
#                 """
#             db.cur.execute(q, appname)

#         r = db.cur.fetchone()
#         if r is not None:
#             newpassword = r.newpassword
#             if newpassword is not None and newpassword != '':
#                 pwd = simpledecrypt(newpassword, 8)

#             login = r.loginid

#     except UIException:
#         raise

#     except Exception:
#         raise

#     finally:
#         if db is not None:
#             db.dispose()

#     return login, pwd

# def simpleencrypt(s, seed):
#     sb = []

#     for c in s:
#         i = ord(c)
#         i = i - seed
#         sb.append(chr(i))

#     r = ''.join(sb)
#     return string2hex(r)

# def simpledecrypt(s, seed):
#     psw = hex2string(s)
#     sb = []

#     for c in psw:
#         value = ord(c)
#         value += seed
#         ch = chr(value)
#         sb.append(ch)

#     return ''.join(sb)

# def hex2string(strhex):
#     n = len(strhex)
#     sb = []

#     if (n % 2) != 0:
#         raise UIException('Data string is corrupted.  Cannot be Decrypted.')

#     i = 0
#     while i < n:
#         hexvalue = strhex[i:i + 2]
#         value = int(hexvalue, 16)
#         charvalue = chr(value)
#         sb.append(charvalue)
#         i += 2

#     return ''.join(sb)

# def string2hex(str):
#     sb = []

#     for c in str:
#         t = '00' + hex(ord(c))
#         r = t[-2:]
#         sb.append(r)

#     return ''.join(sb).upper()

# def fromjson(req):
#     return json.loads(req.body, encoding='utf-8')

# def decode(s):
#     x = s

#     if s is not None:
#         if isinstance(s, str):
#             x = s.strip('\r\n')

#     return x

# def getrandomnum(x):
#     return random.randint(0, x)

# def gensippassword():
#     buff = 'ABCDEFGHIJKLMNOPQRSTUVQXYZ'
#     buff += buff.lower()
#     buff += '0123456799'
#     l = len(buff)
#     s = ''

#     #pswlen = getrandomnum(6) + 15
#     pswlen = 15

#     for i in range(pswlen):
#         k = getrandomnum(l)
#         s += buff[k:k + 1]

#     return s

# def iscallshoptype(subtype):
#     b = False
#     x = int(subtype)

#     if x >= constants.CALLSHOPSUBTYPE1 and x <= constants.CALLSHOPSUBTYPE2:
#         b = True

#     return b

# def iscredittransfer(topuptype):
#     b = False
#     x = int(topuptype)

#     if x == constants.CREDIT_TRANSFER:
#         b = True

#     return b

# def removequotation(s):
#     if s is None:
#         return s

#     r = s.replace("'", "").replace('"', '').strip()
#     return r

# def isallowperformtopup(topuptype, accesslevel):
#     b = True
#     x = int(topuptype)

#     if x == 1:
#         if accesslevel != 2 and accesslevel != 4:
#             b = False

#     return b

# def isallowsyncbalance(accesslevel):
#     return True if accesslevel in [100, 1, 2, 3, 4] else False

# def isadmin(flag):
#     return True if flag[constants.FEATUREBIT.DELETE] != '0' else False

# def isnewvisible(flag):
#     return True if flag[constants.FEATUREBIT.ADDNEW] != '0' else False

# def isupdatevisible(flag):
#     return True if flag[constants.FEATUREBIT.UPDATE] != '0' else False

# def istopupreportvisible(flag):
#     return True if flag[constants.FEATUREBIT.TOPUPREPORT] != '0' else False

# def iscontactlistvisible(flag):
#     return True if flag[constants.FEATUREBIT.CONTACTLIST] != '0' else False

# def isdeletevisible(flag):
#     return True if flag[constants.FEATUREBIT.DELETE] != '0' else False

# def isothervisible(flag):
#     return True if flag[constants.FEATUREBIT.MORE] != '0' else False

# def istechinfovisible(flag):
#     return True if flag[constants.FEATUREBIT.TECHNICALINFO] != '0' else False

# def isresetiddusagevisible(flag):
#     return istechinfovisible(flag)

# def is015pwdvisible(flag):
#     return True if flag[constants.FEATUREBIT.SHOW015PASSWORD] == '1' else False

# def isminikiosk(subtype):
#     i = int(subtype)
#     b = True if i in constants.KIOSKCALLERIDBLOCKINGTYPE else False
#     return b

# def isvkiosktype(subtype):
#     i = int(subtype)
#     b = True if i == constants.VKIOSKTYPE else False
#     return b

# def checkaccesslevel(accesslevel):
#     dic = {}

#     if accesslevel == 100:
#         dic[constants.ACCESS.TOPUPREPORT] = 1
#         dic[constants.ACCESS.CHANGEGATETYPE] = 1
#         dic[constants.ACCESS.ADDREMARK] = 1

#     elif accesslevel == 1:
#         dic[constants.ACCESS.TOPUPREPORT] = 1

#     elif accesslevel == 2:
#         dic[constants.ACCESS.TOPUPREPORT] = 1
#         dic[constants.ACCESS.CHANGEGATETYPE] = 1
#         dic[constants.ACCESS.ADDREMARK] = 1

#     elif accesslevel in [3, 4]:
#         dic[constants.ACCESS.TOPUPREPORT] = 1
#         dic[constants.ACCESS.ADDREMARK] = 1

#     return dic

# def checkemptyuserdetail(d):
#     accountid = d.get('accountid', '').strip()
#     name = d.get('name', '').strip()

#     if accountid == '':
#         raise UIException('Data not Complete (Customer AccountID)...')

#     if name == '':
#         raise UIException('Data not Complete (Customer Name)...')

#     if d['imaintype'] is None:
#         raise UIException('Data not Complete (MainType)...')

#     if d['isubtype'] is None:
#         raise UIException('Data not Complete (SubType)...')

#     if d['iratetype'] is None:
#         raise UIException('Data not Complete (Rate Type)...')

#     if d['igatetype'] is None:
#         raise UIException('Data not Complete (Gateway Type)...')

#     if d['ilang'] is None:
#         raise UIException('Data not Complete (Language)...')

#     if d['ilcrtype'] is None:
#         raise UIException('Data not Complete (LCR Type)...')

#     if d['wholesalerkey'] is None:
#         raise UIException('Please select a wholesaler for this account')

# def isduplicatekey(s):
#     return True if str(s).find('insert duplicate key') != -1 else False

# def sendfile(b, filename, content_type):
#     r = HttpResponse(b, content_type=content_type)
#     r['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename)
#     return r

# def sendfileinline(b, filename, content_type):
#     r = HttpResponse(b, content_type=content_type)
#     r['Content-Disposition'] = 'inline; filename="{0}"'.format(filename)
#     return r

class UIException(Exception):
    pass
