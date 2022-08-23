import psycopg2
from psycopg2 import Error
from datetime import datetime

con = psycopg2.connect(
        user = "postgres",
        password = "postgres",
        host = "127.0.0.1",
        database ="db"
        )

cur = con.cursor()

def initialize():

    cur.execute(''' CREATE TABLE IF NOT EXISTS leaves
    (eid text not null ,
     lid text not null ,
     starting_date date not null ,
     ending_date date not null,
     status text not null,
     next text not null ,
     borrow integer not null 
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS leave_hierarchy
    (child text not null ,
     parent text not null,
     for_whom text not null
     );''')

    cur.execute(''' CREATE TABLE IF NOT EXISTS comment
    ( approved_on date not null,
      eid text not null ,
      lid text not null,
      response text not null,
      ctext text not null
     );''')

    con.commit()

def can_apply(eid):
        status='pending'
        cur.execute(''' select count(*) from leaves where eid = %s and status=%s;''',(eid,status))
        n=cur.fetchone()
        if n[0]==0 :
                return 1
        else :
                return 0

def get_position(user):
        cur.execute(''' select count(*) from hod where eid =%s ;''',(user,))
        n=cur.fetchone()
        pos='faculty'
        if n[0] == 1:
                pos='hod'
        cur.execute(''' select count(*) from cross_cutting where eid =%s; ''',(user,))
        n=cur.fetchone()
        if n[0]==1:
                cur.execute(''' select designation from cross_cutting where eid =%s; ''',(user,))
                l=cur.fetchone()
                return(l[0])
        return pos

def next_hierarchy(pos,for_whom):
        cur.execute(''' select count(*) from leave_hierarchy where for_whom =%s and child=%s;''',(for_whom,pos))
        l=cur.fetchone()
        if l[0]==0 :
                s='null'
                return s
        cur.execute(''' select * from leave_hierarchy where for_whom =%s and child=%s;''',(for_whom,pos))
        n=cur.fetchone()
        return(n[1])

def apply(user,sd,ed,ct):
        cur.execute(''' select count(*) from leaves ;''')
        n=cur.fetchone()
        pos = get_position(user)
        next=next_hierarchy(pos,pos)
        sd=datetime.strptime(sd,"%Y-%m-%d")
        ed=datetime.strptime(ed,"%Y-%m-%d")
        l=abs((ed-sd).days)        
        cur.execute('''select nol from employee where eid =%s;''',(user,))
        leaves_left=cur.fetchone()
        borrow =0
        if leaves_left[0] <l:
                borrow=leaves_left[0]-l
        status='pending'
        cur.execute('''insert into leaves (eid,lid,starting_date,ending_date,status,next,borrow) values (%s,%s,%s,%s,%s,%s,%s)''',(user,n[0]+1,sd,ed,status,next,borrow))
        con.commit()
        cur.execute(''' select count(*) from comment ;''')
        c=cur.fetchone()
        time=datetime.now()


        response='none'
        cur.execute('''insert into comment (approved_on,lid,eid,response,ctext) values (%s,%s,%s,%s,%s)''',(time,n[0]+1,user,response,ct))
        con.commit()

def get_dept(user):
        cur.execute(''' select department from hod where eid=%s ;''',(user,))
        d=cur.fetchone()
        return d[0]

def get_name(user):
        cur.execute(''' select name from employee where eid=%s ;''',(user,))
        d=cur.fetchone()
        return d[0]

def get_eid(lid):
         cur.execute(''' select eid from leaves where lid=%s ;''',(lid,))
         n=cur.fetchone()
         return n[0]
         
def get_leaves_to_comment(user):
        pos=get_position(user)
        #print(user+ "...................................")
        status ='pending'
        if pos=='hod':
                d=get_dept(user)
                d1=dict()
                cur.execute('''select leaves.eid,lid,starting_date,ending_date,borrow from leaves,faculty where leaves.eid=faculty.eid and department=%s and status=%s and next=%s;''',(d,status,pos))
                i=1
                rows=cur.fetchall()
                for row in rows:
                        d2=dict()
                        
                        d2['Empoyee Id']=row[0]
                        d2['Leave_id']=row[1]
                        d2['Starting_date']=row[2]
                        d2['Ending_date']=row[3]
                        d2['Leaves_to_be_borrowed']=row[4]
                        d2['Name']=get_name(get_eid(row[1]))
                        d1[i]=d2
                        i+=1
                return(d1)
        else:
                cur.execute('''select * from leaves where status=%s and next=%s;''',(status,pos))
                i=1
                d1=dict()
                rows=cur.fetchall()
                for row in rows:
                        d2=dict()
                        d2['Empoyee Id']=row[0]
                        d2['Leave_id']=row[1]
                        d2['Starting_date']=row[2]
                        d2['Ending_date']=row[3]
                        d2['Leaves_to_be_borrowed']=row[4]
                        d2['Name']=get_name(get_eid(row[1]))
                        d1[i]=d2
                        i+=1
                return(d1)
        
def can_comment(user,lid):
        pos=get_position(user)
        status='pending'
        if pos=='hod':
                d=get_dept(user)
                cur.execute('''select count(*) from leaves,faculty where leaves.eid=faculty.eid and department=%s and status=%s and next=%s and lid=%s;''',(d,status,pos,lid))
                n=cur.fetchone()
                if n[0]==1:
                        return 1
                else :
                        return 0
        else:
                cur.execute('''select count(*) from leaves where status=%s and next=%s and lid=%s;''',(status,pos,lid))
                n=cur.fetchone()
                if n[0]==1:
                        return 1
                else:
                        return 0

def get_leave_applicant(lid):
        cur.execute('''select eid from leaves where lid=%s;''',(lid))
        n=cur.fetchone()
        return n[0]


def get_no_of_days(lid):
        cur.execute('''select starting_date,ending_date from leaves where lid=%s;''',(lid))
        n=cur.fetchone()
        return((n[1]-n[0]).days)

def add_comment(user,lid,ctext,response):
        time=datetime.now()
        cur.execute('''insert into comment (approved_on,lid,eid,response,ctext) values (%s,%s,%s,%s,%s)''',(time,lid,user,response,ctext))
        con.commit()
        pos=get_position(user)
        for_whom=get_position(get_leave_applicant(lid))
        next=next_hierarchy(pos,for_whom)
        if response=='revert':
                next=get_position(get_leave_applicant(lid))
                cur.execute('''update leaves set next=%s where lid=%s''',(next,lid))
                status='pending'
                cur.execute('''update leaves set status=%s where lid=%s''',(status,lid))
                con.commit()
                return 
                
        if next=='null':
                status='rejected'
                if response=='yes':
                        status='approved'
                        cur.execute('''select nol from employee where eid=%s;''',(get_leave_applicant(lid),))
                        n=cur.fetchone()
                        l=int(n[0])-int(get_no_of_days(lid))
                        cur.execute('''update  employee set nol=%s where eid=%s''',(l,get_leave_applicant(lid)))
                        con.commit()
                cur.execute('''update leaves set status=%s where lid=%s''',(status,lid))
                con.commit()
        else:
                status='pending'
                if response=='no':
                        status='rejected'
                cur.execute('''update leaves set status=%s where lid=%s''',(status,lid))
                con.commit()
        cur.execute('''update leaves set next=%s where lid=%s''',(next,lid))
        con.commit()
        
        
def reCommentCheck(user):
        pos=get_position(user)
        status = 'pending'
        cur.execute('''select lid from leaves where eid = %s and status = %s and next = %s ;  ''',(user,status,pos))
        rowcount = cur.rowcount
        if(rowcount>0):
                n=cur.fetchone()
                l_id=n[0]
                return l_id
                
        else:
            return -1
            #no such pending leave where to recomment
            

def reComment(user,l_id,commnt):
        pos=get_position(user)
        time=datetime.now()
        response='pending'
        cur.execute("insert into comment (approved_on,lid,eid,response,ctext) values (%s,%s,%s,%s,%s)",(time,l_id,user,response,commnt))
        con.commit()
        superior = next_hierarchy(pos,pos)
        cur.execute("update  leaves set next = %s where lid = %s",(superior,l_id))
        con.commit()
        return

def get_status(user):
        stat = 'pending'
        cur.execute("select lid from leaves where status = %s and eid = %s;",(stat,user))
        rowcount = cur.rowcount
        if(rowcount>0):
                n=cur.fetchone()
                return n[0]
        else:
                return 'None'


def stats(user):
        cur.execute("select * from leaves where eid = %s;",(user,))
        rows = cur.fetchall()
        r,c = (len(rows),2)
        a = [[0 for i in range(c)] for j in range(r)] 
        d=dict()
        i=0
        for row in rows:
                a[i][0]=row[4]
                a[i][1]=row[5]
                d[row[1]]=a[i]
                i+=1

        return d

def viewCommentsOnMyLeaves(user):
        cur.execute("select * from leaves where eid=%s;",(user,))
        rows1=cur.fetchall()
        d=dict()
        for row1 in rows1:
                lid=row1[1]
                cur.execute("select approved_on,eid,response,ctext from comment where lid = %s;",(lid,))
                rows2 = cur.fetchall()
                d[lid]=rows2             

        return d

def latestLeave(user):
        cur.execute("select status from leaves where eid=%s;",(user,))
        rowcount = cur.rowcount
        if(rowcount<=0):
                return None
        rows1=cur.fetchall()
        for row1 in rows1:
                status=row1[0]
        return status