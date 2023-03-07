"""Validator Module"""
import re
# from bson.objectid import ObjectId

def validate(data, regex):
    """Custom Validator"""
    return True if re.match(regex, data) else False

def validate_password(password: str):
    """Password Validator"""
    reg = r"\b^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,20}$\b"
    return validate(password, reg)

def validate_email(email: str):
    """Email Validator"""
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    return validate(email, regex)

def validate_user(**args):
    """User Validator"""
    if  not args.get('email') or not args.get('password') or not args.get('name'):
        return {
            'email': 'Email is required',
            'password': 'Password is required',
            'name': 'Name is required'
        }
    if not isinstance(args.get('name'), str) or \
        not isinstance(args.get('email'), str) or not isinstance(args.get('password'), str):
        return {
            'email': 'Email must be a string',
            'password': 'Password must be a string',
            'name': 'Name must be a string'
        }
    if not validate_email(args.get('email')):
        return {
            'email': 'Email is invalid'
        }
    if not validate_password(args.get('password')):
        return {
            'password': 'Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters'
        }
    if not 2 <= len(args['name'].split(' ')) <= 30:
        return {
            'name': 'Name must be between 2 and 30 words'
        }
    return True

def validate_email_and_password(email, password):
    """Email and Password Validator"""
    if not (email and password):
        return {
            'email': 'Email is required',
            'password': 'Password is required'
        }
    if not validate_email(email):
        return {
            'email': 'Email is invalid'
        }
    if not validate_password(password):
        return {
            'password': 'Password is invalid, Should be atleast 8 characters with \
                upper and lower case letters, numbers and special characters'
        }
    return True



def validate_user_form(username, password, email,groupid,siteid):

    if not (username and password and email and groupid and siteid):
        return {
            'username': 'Username is required',
            'password': 'Password is required',
            'email': 'Email is required',
            'groupid': 'Group is required',
            'siteid': 'Default site is required',

        }
    return True

def validate_penandaan_semp_form(hutansimpan_id, kompatmen,pokokstesen, spesies):
    if not (hutansimpan_id and kompatmen  and pokokstesen and spesies ):
        return {
            'hutansimpan_id': 'Hutan Simpan is required',
            'kompatmen': 'Kompatmen X is required',
            'pokokstesen': 'Stesen Value  is required',
            'spesies': 'Spesies Pokok is required',
            

        }
    return True

def validate_createhutan(state, district,type,name, keluasan):
    if not (state and district and type and name and keluasan):
        return {
            'state': 'State selection is required',
            'district': 'District selection is required',
            'type': 'Type is required',
            'name': 'Name  is required',
            'keluasan': 'Keluasan Hutan is required'
           

        }
    return True

def validate_createkompatmen(name_code):

    if not (name_code):
        return {
            'name_code': 'name is required',


        }
    return True

def validate_createfamilyspesis(name,kumpulan_d_nd):

    if not (name  and kumpulan_d_nd ):
        return {
            'name': 'Spesis Name is required',
            'kumpulan_d_nd': 'Spesis Type is required',
            


        }
    return True    

def validate_createsubspesis(family_id,local_name,scientific_name):

    if not (family_id and local_name and scientific_name):
        return {
            'family_id': 'Spesis Family is required',
            'local_name': 'Local Name is required',
            'scientific_name': 'Scientific Name is required',


        }
    return True   

def validate_bancian_pre_tebangan(kompatment_id,no_pokok,dbh,spesies,pepanjat,bil_tual):

    if not (kompatment_id and no_pokok and dbh and spesies and pepanjat and bil_tual):
        return {
            'kompatment_id': 'Kompatmen ID is required',
            'no_pokok': 'Pokok ID is required',
            'dbh': 'DBH is required',
            'spesies': 'Spesis is required',
            'pepanjat': 'Pepanjat Value is required',
            'bil_tual': 'Bil Tual is required',


        }
    return True   

def validate_bancian_selepas_tebangan(kompatment_id,no_pokok,no_tag,dbh,spesies,bil_tual):

    if not (kompatment_id and no_pokok and no_tag and dbh and spesies and bil_tual):
        return {
            'kompatment_id': 'Kompatmen ID is required',
            'no_pokok': 'Pokok ID is required',
            'no_tag': 'NFC ID is required',
            'dbh': 'DBH is required',
            'spesies': 'Spesis is required',
            'bil_tual': 'Bil Tual is required',


        }
    return True   


def validate_add_rawatan(kompatment_id,jenis_rawatan,tahun):

    if not (kompatment_id and jenis_rawatan and tahun):
        return {
            'kompatment_id': 'Kompatmen ID is required',
            'jenis_rawatan': 'Jenis Rawatan is required',
            'tahun': 'Tahun is required',
            

        }
    return True  

def validate_penandaanpokok(kompatmen_id,no_pokok,no_tag,spesies_id,dbh,bil_tual):

    if not (kompatmen_id and no_pokok and no_tag and spesies_id and dbh and bil_tual ):
        return {
            'kompatmen_id': 'Kompatmen ID is required',
            'no_pokok': 'Pokok ID is required',
            'no_tag': 'Tag ID is required',
            'spesies_id': 'Spesis is required',
            'dbh': 'DBH is required',           
            'bil_tual': 'Bil Tual is required',

        }
    return True  


def validate_update_penandaanpokok(kompatmen_id,no_pokok,spesies_id,dbh,bil_tual):

    if not (kompatmen_id and no_pokok and spesies_id and dbh and bil_tual ):
        return {
            'kompatmen_id': 'Kompatmen ID is required',
            'no_pokok': 'Pokok ID is required',
            'spesies_id': 'Spesis is required',
            'dbh': 'DBH is required',            
            'bil_tual': 'Bil Tual is required',

        }
    return True  



def validate_banciantinggal(no_pokok,dbh,status_pokok,jenis_kerosakan,tahap_kerosakan):

    if not (no_pokok and  dbh  and status_pokok and jenis_kerosakan and tahap_kerosakan ):
        return {
            'no_pokok': 'Pokok ID is required', 
            'dbh': 'DBH is required',
            'status_pokok': 'Status Pokok is required',
            'jenis_kerosakan': 'Jenis Kerosakan Y is required',            
            'tahap_kerosakan': 'Tahap Kerosakan is required',

        }
    return True  

def validate_pembalakaddTual(no_pokok,nfc_tag,no_tual,panjang,dbh):

    if not (no_pokok and  nfc_tag  and no_tual and panjang and dbh ):
        return {
            'no_pokok': 'Pokok ID is required', 
            'nfc_tag': 'DBH is required',
            'no_tual': 'Status Pokok is required',
            'panjang': 'Jenis Kerosakan Y is required',            
            'dbh': 'Tahap Kerosakan is required',

        }
    return True  

def validate_price_data(spesies_id,price):

    if not (spesies_id and  price):
        return {
            'spesies_id': 'Pokok ID is required', 
            'price': 'Price value is required',
            
        }
    return True 

def validate_body_value(body):
    if not (body ):
        return {
            'body': 'body is required'
        }
    return True