import psycopg2
from psycopg2 import Error
from datetime import datetime
leaves=25

con = psycopg2.connect(
        user = "postgres",
        password = "postgres",
        host = "127.0.0.1",
        database ="db"
        )

cur = con.cursor()

def initialize():

    cur.execute(''' CREATE TABLE IF NOT EXISTS employee
    (eid text not null ,
     password text not null ,
     name text not null ,
     doj date not null,
     email text not null,
     nol int not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS faculty
    (eid text not null ,
     department text not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS hod
    (eid text not null,
     department text not null 
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS cross_cutting
    (eid text not null ,
     designation text not null 
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS pos_history
    (eid text not null ,
     type text not null ,
     desg_or_dept text not null ,
     start_date date not null,
     end_date date not null
     );''')

    print('Tables created..........................................')

    con.commit()

def insert_faculty(eid,password,name,doj,email):
    cur.execute('''insert into employee (eid,password,name,email,doj,nol) values (%s,%s,%s,%s,%s,%s)''',(eid,password,name,email,doj,leaves))
    #cur.execute('''insert into faculty (eid,department) values (%s,%s)''',(eid,department))
    con.commit()
    return None

def verify_credentials(id,passw):
    cur.execute('''select count(*) from employee where eid = %s and password = %s  ;  ''',(id,passw))
    
    n = cur.fetchone()
    if n[0] == 1 :
        return 1
    else:
        return 0

def fetch_employee(id):
    cur.execute('''select * from employee where eid= %s ;''',(id,))
    n = cur.fetchone()
    d =dict()
    d['Employee id'] =n[0]
    d['Name']=n[2]
    d['DOJ']=n[3]
    d['Email']=n[4]
    d['Leaves_left']=n[5]
    return d

def fetch_all_details():
    cur.execute('''select name,eid from employee;''')
    n=cur.fetchall()
    d=dict()
    i=1
    for rows in n:
        d1=dict()
        d1['Name--->']=rows[0]
        d1['Employee id--->']=rows[1]
        d[i]=d1
        i+=1
    return d

#def insert_hod(eid,password,name,department,doj,):
    #cur.execute('''insert into hod (fid,password,name,department) values(%s,%s,%s,%s)''' ,(fid,password,name,department))
   # con.commit()

#def insert_cross_cutting(eid,name,passw ord,):
     #cur.execute('''insert into cross_cutting(fid,password,name,designation) values(%s,%s,%s,%s)''' ,(fid,password,name,designation))
     #con.commit()

