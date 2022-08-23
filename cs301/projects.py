import psycopg2
from datetime import datetime

con = psycopg2.connect(
        user = "postgres",
        password = "postgres",
        host = "127.0.0.1",
        database ="db"
        )

cur = con.cursor()

def initialize():

    cur.execute(''' CREATE TABLE IF NOT EXISTS project
    (pid text not null ,
     eid text not null ,
     manpower integer not null ,
     equipment integer not null,
     travel integer not null
     );''')
     
    cur.execute(''' CREATE TABLE IF NOT EXISTS copi_table
    (pid text not null,
     eid text not null 
     );''')


    cur.execute(''' CREATE TABLE IF NOT EXISTS application
    (aid text not null ,
     eid text not null ,
     pid text not null,
     date_of_issue date not null ,
     no_of_months integer not null,
     status text not null,
     next text not null ,
     type_of_app text not null,
     name_of_agency text not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS app_hierarchy
    (child text not null ,
     parent text not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS comment_app
    ( approved_on date not null,
      eid text not null ,
      aid text not null,
      response text not null,
      ctext text not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS agency
    (name text not null ,
     manpower integer not null ,
     equipment integer not null,
     travel integer not null
     );''')     

    cur.execute(''' CREATE TABLE IF NOT EXISTS expenditure
    (pid text not null ,
     manpower integer not null ,
     equipment integer not null,
     travel integer not null
     );''')

    con.commit()

def check_dup_entry(user,pid,typee,nom,agency):
        status = 'pending'
        cur.execute(''' select count(*) from application where eid = %s and pid=%s and type_of_app=%s and no_of_months=%s and name_of_agency=%s and status = %s;''',(user,pid,typee,nom,agency,status))
        n=cur.fetchone()
        if n[0]==1:
                return 1
        else:
                return 0


def get_position(user,pid):
        cur.execute(''' select count(*) from project where eid= %s and pid=%s;''',(user,pid))
        n=cur.fetchone()
        if n[0]==1:
                return('mainpi')
        cur.execute(''' select count(*) from copi_table where eid= %s and pid=%s;''',(user,pid))
        n=cur.fetchone()
        if n[0]==1:
                return('copi')
        cur.execute(''' select * from cross_cutting where eid= %s ;''',(user,))
        n=cur.fetchone()
        return n[1]

def get_next(user,pid):
        pos=get_position(user,pid)
        cur.execute(''' select count(*) from app_hierarchy where child=%s ;''',(pos,))
        n=cur.fetchone()
        if n[0]==0:
                return('null')
        cur.execute(''' select parent from app_hierarchy where child=%s ;''',(pos,))
        n=cur.fetchone()
        return(n[0])

def check_correct_user(user,pid):
        cur.execute(''' select * from project where eid=%s and pid=%s ;''',(user,pid))
        rowcount = cur.rowcount
        if(rowcount>0):
                return 1
        cur.execute(''' select * from copi_table where eid=%s and pid=%s ;''',(user,pid))
        rowcount=cur.rowcount
        if(rowcount>0):
                return 1
        return 0

def check_agency(ag,typee):
        cur.execute(''' select * from agency where name=%s ;''',(ag,))
        rowcount = cur.rowcount
        if(rowcount>0):
                n=cur.fetchone()
                if typee=='manpower':
                        return n[1]
                elif typee=='equipment':
                        return n[2]
                else:
                        return n[3]
        else:
                return 0

def get_type_price(pid,typee):
        cur.execute(''' select *from project where pid=%s ;''',(pid,))
        n=cur.fetchone()
        if typee=='manpower':
                return n[2]
        elif typee=='equipment':
                return n[3]
        else:
                return n[4]


def add_entry(user,pid,typee,nom,agency,ctext):
        d=dict()

        f=check_correct_user(user,pid)
        if f==0:
                d['status']='You are not allowed to raise the request'
                return d
        f=check_dup_entry(user,pid,typee,nom,agency)
        if f==1:
                d['status:']='Sorry duplicate entry'
                return d
        f=check_agency(agency,typee)
        if f==0:
                d['status']='Incorrect request raised'
                return d
        p=get_type_price(pid,typee)
        if (int(p) <(int(f)*int(nom))):
                d['status']='Insufficient fund'
                return d

        cur.execute(''' select count(*) from application ;''')
        n=cur.fetchone()
        date=datetime.now()
        status='pending'
        next=get_next(user,pid)
        cur.execute('''insert into application (aid,eid,pid,date_of_issue,no_of_months,status,next,type_of_app,name_of_agency) values (%s,%s,%s,%s,%s,%s,%s,%s,%s);''',(n[0]+1,user,pid,date,nom,status,next,typee,agency))
        con.commit()
        status='none'
        cur.execute('''insert into comment_app (aid,eid,response,ctext,approved_on) values (%s,%s,%s,%s,%s);''',(n[0]+1,user,status,ctext,date))
        con.commit()
        d=dict()
        d['status:']='request raised successfully'
        return(d)

def application_to_comment(user):
        status='pending'
        cur.execute(''' select aid ,pid,next from application where status=%s;''',(status,))
        r=cur.fetchall()
        d=dict()
        i=1
        for rows in r:
                my_pos=get_position(user,rows[1])
                if my_pos==rows[2] :
                        d1=dict()
                        cur.execute(''' select aid ,pid,date_of_issue,no_of_months,type_of_app,name_of_agency from application where aid=%s;''',(rows[0],))
                        n=cur.fetchone()
                        d1['Application id:']=n[0]
                        d1['Project id:']=n[1]
                        d1['Date of issue:']=n[2]
                        d1['No of months:']=n[3]
                        d1['Type of application:']=n[4]
                        d1['Name of agency:']=n[5]
                        d[i]=d1 
                i+=1        
        return(d)
        
def can_comment(aid,user):
        cur.execute(''' select pid ,next from application where aid=%s;''',(aid,))
        rowcount=cur.rowcount
        if (rowcount==0):
                return 0
        n=cur.fetchone()
        pos=get_position(user,n[0])
        if pos==n[1]:
                return 1
        else:
                return 0
        
def get_pid(aid):
        cur.execute(''' select pid from application where aid=%s;''',(aid,))
        n=cur.fetchone()
        return n[0]             

def get_type(aid):
        cur.execute(''' select type_of_app from application where aid=%s;''',(aid,))
        n=cur.fetchone()
        return(n[0])

def get_nom(aid):
        cur.execute(''' select no_of_months from application where aid=%s;''',(aid,))
        n=cur.fetchone()
        return(n[0])

def get_agency_price(aid,typee):
        cur.execute(''' select name_of_agency from application where aid=%s;''',(aid,))
        n=cur.fetchone()
        cur.execute(''' select * from agency where name=%s;''',(n[0],))
        n=cur.fetchone()
        if typee=='manpower':
                return n[1]
        elif typee=='equipment':
                return n[2]
        else:
                return n[3]

def add_expenditure(aid,pid):
        typee=get_type(aid)
        price=get_type_price(pid,typee)
        nom=get_nom(aid)
        cur.execute(''' select * from expenditure where pid=%s;''',(pid,))
        n=cur.fetchone()
        p=get_agency_price(aid,typee)
        #print("p = "+p+" nom = "+nom+" price = "+price+" type = "+typee+" ")
        if typee=='manpower':
                e=n[1]+nom*p
                cur.execute('''update expenditure set manpower=%s where pid=%s;''',(e,pid))
                con.commit()
                cur.execute('''update project set manpower=%s where pid=%s;''',(price-nom*p,pid))
                con.commit()
        elif typee=='equipment':
                e=n[2]+nom*p
                cur.execute('''update expenditure set equipment=%s where pid=%s;''',(e,pid))
                con.commit()
                cur.execute('''update project set equipment=%s where pid=%s;''',(price-nom*p,pid))
                con.commit()
        else :
                e=n[3]+nom*p
                cur.execute('''update expenditure set travel=%s where pid=%s;''',(e,pid))
                conInsufficient .commit()
                cur.execute('''update project set travel=%s where pid=%s;''',(price-nom*p,pid))
                con.commit()
        print(",,,,,,,,,,<<<<<<<<<<<<")
        print(e)

def add_comment(aid,user,ctext,response):
        f=can_comment(aid,user)
        if f==0:
                return ('commenting failed')
        
        nom=get_nom(aid)
        typee=get_type(aid)
        pid=get_pid(aid)
        price=get_type_price(pid,typee)
        p=get_agency_price(aid,typee)
        if (price <p*nom):
                cur.execute('''update application set status=%s where aid=%s;''',('rejected',aid))
                con.commit()
                return ('Insufficientfund')
        date=datetime.now()
        cur.execute('''insert into comment_app (aid,eid,response,ctext,approved_on) values (%s,%s,%s,%s,%s);''',(aid,user,response,ctext,date))
        con.commit()

        if response=='no':
                cur.execute('''update application set status=%s where aid=%s;''',('rejected',aid))
                con.commit()
                next='null'
                cur.execute('''update application set next=%s where aid=%s;''',('null',aid))
                con.commit()
        else:
                pid=get_pid(aid)
                next=get_next(user,pid)
                if next=='null':
                        cur.execute('''update application set status=%s where aid=%s;''',('approved',aid))
                        con.commit()
                        add_expenditure(aid,pid)
                cur.execute('''update application set next=%s where aid=%s;''',(next,aid))
                con.commit()      
        return('Commenting successful')

def showAllExpend():
        cur.execute("select count(*) from expenditure;")
        n=cur.fetchone()
        cur.execute("select pid from expenditure;") 
        l=cur.fetchall()      

        d1=dict() 
        rows, cols = (n[0], 3) 
        a = [[0 for i in range(cols)] for j in range(rows)] 
        print("/////////////////////////////")
        cur.execute("select * from expenditure;") 
        i=0
        l=cur.fetchall()
        for row in l:
                a[i][0]=row[1]
                a[i][1]=row[2]
                a[i][2]=row[3]
                d1[row[0]]=a[i]
                i=i+1

        return d1

def isPi(user):
        cur.execute("select count(*) from project where eid = %s;",(user,))
        n=cur.fetchone()
        if(n[0]==0):
                cur.execute("select count(*) from copi_table where eid = %s;",(user,))
                n=cur.fetchone()    
                if(n[0]==0):
                        return 0
                else:
                        return 1    
        else:
                return 1

def stats(user):
        cur.execute("select * from application where eid = %s;",(user,))
        rows = cur.fetchall()
        r,c = (len(rows),6)
        a = [[0 for i in range(c)] for j in range(r)] 
        d=dict()
        i=0
        for row in rows:
                a[i][0]=row[2]
                a[i][1]=row[4]
                a[i][2]=row[5]
                a[i][3]=row[6]
                a[i][4]=row[7]
                a[i][5]=row[8]
                d[row[1]]=a[i]
                i+=1

        return d

