import mysql.connector

def disposedb(con, cur):
    if cur is not None:
        cur.close()

    if con is not None:
        con.close()

def initdb():
    con = mysql.connector.connect(host='10.80.10.39', user='frim', password='P@ssw0rd2288',  database='FRIM')
    cur = con.cursor()
    return con, cur


