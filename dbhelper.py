import mysql.connector

def disposedb(con, cur):
    if cur is not None:
        cur.close()

    if con is not None:
        con.close()

def initdb():
    con = mysql.connector.connect(host='####', user='##', password='##',  database='##')
    cur = con.cursor()
    return con, cur


