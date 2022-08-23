from flask import Flask, redirect ,url_for, request ,render_template, session
import psycopg2
import fun 
import leaves
import psycopg2
from flask import Flask, redirect, url_for, request,Flask, render_template, request, flash
from adminForms import adminWorks,hodTable,crossCuttingTable,facultyTable,leaveHTable,projectTable,copiTable,agencyTable,appHTable
import psycopg2
from config import config
import helper as st
import mongoengine
from flask_pymongo import PyMongo
import projects
from datetime import datetime


fun.initialize()
leaves.initialize()
projects.initialize()
var= -1
app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/profile/raise_req', methods = [ 'GET' , 'POST' ])
def raise_req():
    if request.method == 'POST':
        user=session.get('user')
        pid = request.form["pid"]
        typee = request.form["type"]
        nom = request.form["nom"]
        agency=request.form['agency']
        ctext=request.form['ctext']
        d=projects.add_entry(user,pid,typee,nom,agency,ctext)
        return render_template('raise_req_status.html',d=d)
    return render_template('raise_req.html')

@app.route('/profile/comment_on_proj',methods=['GET','POST'])
def comment_on_proj():
    if request.method == 'POST':
        user=session.get('user')
        aid=request.form['aid']
        ct=request.form['ctext']
        resp=request.form['response']
        p=projects.add_comment(aid,user,ct,resp)
        return render_template('comment_add_resp.html',p=p)
    return render_template('add_comment_on_proj.html')


def global_init():
    mongoengine.register_connection(alias='chor',name='portal')

@app.route('/')
def welcome():
        return render_template('welcome.html')

@app.route('/direct_to_register_f')
def direct_to_register_f():
    return render_template('register_f.html')

@app.route('/direct_to_login_f')
def direct_to_login_f():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect(url_for('welcome'))

@app.route('/reCommentCheck')
def reCommentCheck():
    user = session.get('user')
    if(leaves.can_apply(user)==0):
        l_id=leaves.reCommentCheck(user)
        if(l_id != -1):
            return redirect(url_for('reCommentFinal',l_id=l_id))

        else:
            return redirect(url_for('profile'))
            #no such  leave where to recomment
    else:
        return redirect(url_for('profile'))
        #no pending leaves

@app.route('/profile/can_approve')
def can_approve():
    user=session.get('user')
    d=projects.application_to_comment(user)
    return render_template('can_approve.html',d=d)


@app.route('/reCommentFinal/<l_id>', methods = [ 'GET' , 'POST' ])
def reCommentFinal(l_id):
    user = session.get('user')
    if request.method == 'POST':
        commnt = request.form["reCmnt"]
        leaves.reComment(user,l_id,commnt)
        return redirect(url_for('profile')) #add msg
    return render_template('reComment.html',lid=l_id)

@app.route('/profile/comment_on_leaves',methods=['GET','POST'])
def comment_on_leaves():
    if request.method == 'POST':
        user=session.get('user')
        lid=request.form['lid']
        ct=request.form['ctext']
        resp=request.form['response']
        flag=leaves.can_comment(user,lid)
        if flag ==0:
            return  redirect(url_for('profile'))
        else:
            leaves.add_comment(user,lid,ct,resp)
            return redirect(url_for('profile'))
    return render_template('comment_on_leaves.html')

@app.route('/profile/apply_for_leaves',methods = [ 'GET' , 'POST' ])
def apply_for_leaves():
    if request.method == 'POST' :
        user=session.get('user')
        flag=leaves.can_apply(user)
        if flag == 1:
            sd=request.form['sdate']
            ed=request.form['edate']
            ct=request.form['comment']
            leaves.apply(user,sd,ed,ct)
            return redirect(url_for('profile'))
        else:
            return render_template('cant_apply.html')       
    return render_template('apply_for_leaves.html')

@app.route('/profile')
def profile():
    user = session.get('user')
    #print(user+"\\\\\\\\\\\\\\\\\\\\\\\\")
    if user:
        emp = fun.fetch_employee(user)
        lv = leaves.latestLeave(user)
        return render_template('profile.html',lv=lv ,emp1 =emp )
    return redirect(url_for('login'))

@app.route('/viewCommentsOnMyLeaves')
def viewCommentsOnMyLeaves():
    user=session.get('user')
    l=leaves.viewCommentsOnMyLeaves(user)
    d="/profile"
    p="Leave id"
    bm=["Commented on","Commented by","Response","Comment"]
    return render_template('viewCommentsOnMyLeaves.html',p=p,l=l,b=bm,dest=d)

@app.route('/viewAppStats')
def viewAppStats():
    user=session.get('user')
    lt=projects.isPi(user)
    if (lt ==0):
        #is not pi
        return ("You are not a pi and cannot see expenditure table.Please redirect to profile")
    l=projects.stats(user)
    d="/profile"
    p="Application id"
    bm=["Project id","Number of months","Status of application","Forwarded to","Type of application","Name of agency"]
    return render_template('showStats.html',p=p,l=l,b=bm,dest=d)


@app.route('/viewLeavesStats')
def viewLeavesStats():
    user=session.get('user')
    d="/profile"
    p="Leave id"
    l=leaves.stats(user)
    bm=["Status","Forwarded to"]
    return render_template('showStats.html',p=p,l=l,b=bm,dest=d)

@app.route('/viewExpend')
def viewExpend():
    user=session.get('user')
    bm=["Manpower","Equipment","Travel"]
    lt=projects.isPi(user)
    d="/profile"
    p="Project id"
    if(lt==1):
        #is pi
        lm=projects.showAllExpend()        
        return render_template('showStats.html',p=p,l=lm,b=bm,dest=d)
    else:
        #is not pi
        return ("You are not a pi and cannot see expenditure table.Please redirect to profile")


@app.route('/update_profile')
def update_profile():
    return render_template('update_profile.html' )

@app.route('/guest')
def guest():
    d=fun.fetch_all_details()
    return render_template('show_all_employees.html',d=d)

@app.route('/guest_profile',methods = ['GET', 'POST'])
def guestProfile():
    if request.method == 'POST':
        fid = request.form['fid']
        login_user = st.find_account_by_fid(fid)
        name1 = login_user.name
        dept = login_user.Department
        email = login_user.email
        doj = login_user.doj
        pubs = login_user.publication
        #return pubs
        pub_size = len(pubs)
        gg = login_user.grants
        g_size = len(gg)
        aa = login_user.awards
        a_size = len(aa)
        tt = login_user.teaching
        t_size = len(tt)
        return render_template('all_guest_profile.html' , fid = fid ,name=name1 ,dept=dept , email=email , doj=doj ,pubs=pubs,gg=gg,aa=aa,tt=tt)
    else:
        return 'Give userid'




@app.route('/view_profile')
def view_profile():
    fid = session.get('user')
    
    #users = mongo.db.users
    login_user = st.find_account_by_fid(fid)
    #login_user = users.find_one({'facultyid' : fid})
    name = login_user.name
    dept = login_user.Department
    email = login_user.email
    doj = login_user.doj
    pubs = login_user.publication
    pub_size = len(pubs)
    gg = login_user.grants
    g_size = len(gg)
    aa = login_user.awards
    a_size = len(aa)
    tt = login_user.teaching
    t_size = len(tt)
    #info = st.getInfo(id)
    return render_template('view_profile.html' , f_id = fid ,name=name ,dept=dept , email=email ,doj=doj, pubs=pubs ,pub_size=pub_size, gg=gg,g_size=g_size,aa=aa,a_size=a_size,tt=tt,t_size=t_size)


@app.route('/edit_publication', methods = ['GET', 'POST'])
def edit_publication():
    user = session.get('user')

    if request.method == 'POST':
        pub = request.form['publication']
        if pub != "":
            st.addPublication(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))


    else:
        return 'please give the imformation' 

@app.route('/delete_publication', methods = ['GET', 'POST'])
def delete_publication():
    user = session.get('user')
    login_user = st.find_account_by_fid(user)
    if request.method == 'POST':
        pub_no = request.form['publication']
        pub_no = int(pub_no)
        pub1 = login_user.publication
        if pub_no-1 < len(pub1):
            pub = pub1[pub_no-1]
            st.deletePublication(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))



    else:
        return 'please give the imformation'

@app.route('/edit_grants', methods = ['GET', 'POST'])
def edit_grants():
    user = session.get('user')

    if request.method == 'POST':
        pub = request.form['grants']
        if pub != "":
            st.addGrants(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))
    else:
        return 'please give the imformation' 

@app.route('/delete_grants', methods = ['GET', 'POST'])
def delete_grants():
    user = session.get('user')
    login_user = st.find_account_by_fid(user)
    if request.method == 'POST':
        pub_no = request.form['grants']
        pub_no = int(pub_no)
        pub1 = login_user.grants
        if pub_no-1 < len(pub1):
            pub = pub1[pub_no-1]
            st.deleteGrants(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))


    else:
        return 'please give the imformation'        

@app.route('/edit_awards', methods = ['GET', 'POST'])
def edit_awards():
    user = session.get('user')

    if request.method == 'POST':
        pub = request.form['awards']
        if pub != "":
            st.addAwards(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))



    else:
        return 'please give the imformation' 

@app.route('/delete_awards', methods = ['GET', 'POST'])
def delete_awards():
    user = session.get('user')
    login_user = st.find_account_by_fid(user)
    if request.method == 'POST':
        pub_no = request.form['awards']
        pub_no = int(pub_no)
        pub1 = login_user.awards
        if pub_no-1 < len(pub1):
            pub = pub1[pub_no-1]
            st.deleteAwards(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))



    else:
        return 'please give the imformation' 

@app.route('/edit_teaching', methods = ['GET', 'POST'])
def edit_teaching():
    user = session.get('user')

    if request.method == 'POST':
        pub = request.form['teching']
        if pub != "":
            st.addTeaching(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))



    else:
        return 'please give the imformation' 

@app.route('/delete_teaching', methods = ['GET', 'POST'])
def delete_teaching():
    user = session.get('user')
    login_user = st.find_account_by_fid(user)
    if request.method == 'POST':
        pub_no = request.form['teaching']
        pub_no = int(pub_no)
        pub1 = login_user.teaching
        if pub_no-1 < len(pub1):
            pub = pub1[pub_no-1]
            st.deleteTeaching(user, str(pub))
            return redirect(url_for('update_profile'))
        else:
            return redirect(url_for('update_profile'))


    else:
        return 'please give the imformation'



@app.route('/profile/status', methods = ['GET', 'POST'])
def status():
    user = session.get('user')
    lid = leaves.get_status(user)
    if(lid == 'None'):
        return ("No pending leaves, please redirect to profile")

    else:
        return ("lid of pending leave = "+lid)


@app.route('/profile/leaves_to_comment')
def leaves_to_comment():
    user=session.get('user')
    l=leaves.get_leaves_to_comment(user)
    return render_template('leaves_to_comment.html',l=l)


@app.route('/login', methods = [ 'GET' , 'POST' ])
def login():
    error=""
    if request.method == 'POST':
        fid = request.form["fid"]
        password = request.form["password"]
        l = fun.verify_credentials(fid,password)
        if l == 0 :
            error="invalid username or password"
        else:
            session['user'] = fid
            return redirect(url_for('profile'))
    return render_template('login.html', error=error)

@app.route('/register', methods = [ 'GET' , 'POST' ])
def register_f():
    if request.method == 'POST':
        fid = request.form["fid"]
        name = request.form["name"]
        password = request.form["password"]
        dept = request.form["department"]
        doj =request.form["doj"]
        email =request.form["email"]
        st.create_account_by_flask(fid,name, password,dept,email,doj)
        fun.insert_faculty(fid,password,name,doj,email)
        return redirect(url_for('welcome'))        
    return redirect(url_for('welcome'))


@app.route('/checkLeaveH',methods = ['GET', 'POST'])
def checkLeaveH():
    form1 = leaveHTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('leaveH.html', form = form1)
                    
        else:
            strName = request.form["child"]
            strCount = request.form["parent"]
            strfr = request.form["forWhom"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO leave_hierarchy(child,parent,for_whom) VALUES(%s,%s,%s)"
                    cur.execute(sql,(strName,strCount,strfr))
                elif(var==2):
                    sql = "update leave_hierarchy set for_whom = %s where child = %s and parent = %s"
                    cur.execute(sql,(strfr,strName,strCount))
                elif(var==3):
                    cur.execute("DELETE FROM leave_hierarchy WHERE for_whom = %s", (strfr,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('leaveH.html', form = form1)



@app.route('/checkFaculty',methods = ['GET', 'POST'])
def checkFaculty():
    form1 = facultyTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('facultyTable.html', form = form1)
                    
        else:
            strName = request.form["username"]
            strCount = request.form["dept"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO faculty(eid,department) VALUES(%s,%s)"
                    cur.execute(sql,(strName,strCount))
                elif(var==2):
                    sql = "update faculty set department = %s where eid = %s"
                    cur.execute(sql,(strCount,strName))
                elif(var==3):
                    cur.execute("DELETE FROM faculty WHERE eid = %s", (strName,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('facultyTable.html', form = form1)



@app.route('/checkCC',methods = ['GET', 'POST'])
def checkCC():
    form1 = crossCuttingTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('crossCuttingTable.html', form = form1)
                    
        else:
            strName = request.form["username"]
            strCount = request.form["desgn"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO cross_cutting(eid,designation) VALUES(%s,%s)"
                    cur.execute(sql,(strName,strCount))
                elif(var==2):
                    #print("/////////////////")
                    cur.execute("select * from cross_cutting where designation =%s;",(strCount,))
                    row1=cur.fetchone()
                    #print("/////////////////"+row1[0])
                    cur.execute("select doj from employee where eid =%s;",(row1[0],))
                    row2=cur.fetchone()
                    #print("/////////////////"+row2[0])
                    date=datetime.now()
                    typ='cross_cutting'
                    cur.execute("insert into pos_history(eid,type,desg_or_dept,start_date,end_date) values(%s,%s,%s,%s,%s);",(row1[0],typ,strCount,row2[0],date))
                    conn.commit()
                    sql = "update cross_cutting set eid = %s where designation = %s"
                    cur.execute(sql,(strName,strCount))
                elif(var==3):
                    cur.execute("DELETE FROM cross_cutting WHERE eid = %s", (strName,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('crossCuttingTable.html', form = form1)


@app.route('/checkHod',methods = ['GET', 'POST'])
def checkHod():
    form1 = hodTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('hodTable.html', form = form1)
                    
        else:
            strName = request.form["username"]
            strCount = request.form["dept"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO hod(eid,department) VALUES(%s,%s)"
                    cur.execute(sql,(strName,strCount))
                elif(var==2):
                    #print("/////////////////")
                    cur.execute("select * from hod where department =%s;",(strCount,))
                    row1=cur.fetchone()
                    #print("/////////////////"+row1[0])
                    cur.execute("select doj from employee where eid =%s;",(row1[0],))
                    row2=cur.fetchone()
                    #print("/////////////////"+row2[0])
                    date=datetime.now()
                    typ='hod'
                    cur.execute("insert into pos_history(eid,type,desg_or_dept,start_date,end_date) values(%s,%s,%s,%s,%s);",(row1[0],typ,strCount,row2[0],date))
                    conn.commit()
                    sql = "update hod set eid = %s where department = %s"
                    cur.execute(sql,(strName,strCount))
                elif(var==3):
                    cur.execute("DELETE FROM hod WHERE eid = %s", (strName,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('hodTable.html', form = form1)


@app.route('/checkProj',methods = ['GET', 'POST'])
def checkProj():
    form1 = projectTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('projectTable.html', form = form1)
                    
        else:
            str_proj = request.form["projId"]
            str_man = request.form["manpower"]
            str_equp = request.form["equip"]
            str_travel = request.form["travel"]
            str_mainId = request.form["mainId"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    cur.execute("select count(*) from project where pid = %s",(str_proj,))
                    n=cur.fetchone()
                    if n[0]==0 :
                            sql = "INSERT INTO project(pid,eid,manpower,equipment,travel) VALUES(%s,%s,%s,%s,%s)"
                            cur.execute(sql,(str_proj,str_mainId,str_man,str_equp,str_travel))
                            sql = "INSERT INTO expenditure(pid,manpower,equipment,travel) VALUES(%s,%s,%s,%s)"
                            cur.execute(sql,(str_proj,0,0,0))
                    else :
                             return ("Name of project already taken ,please enter other name. Reload to admin page")
                    
                elif(var==3):
                    cur.execute("DELETE FROM project WHERE pid = %s;", (str_proj,))
                    cur.execute("DELETE FROM expenditure WHERE pid = %s;", (str_proj,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('projectTable.html', form = form1)

@app.route('/checkCopi',methods = ['GET', 'POST'])
def checkCopi():
    form1 = copiTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('copiTable.html', form = form1)
                    
        else:
            str_proj = request.form["username"]
            str_man = request.form["dept"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO copi_table(pid,eid) VALUES(%s,%s)"
                    cur.execute(sql,(str_proj,str_man))
                elif(var==3):
                    cur.execute("DELETE FROM copi_table WHERE eid = %s", (str_man,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('copiTable.html', form = form1)


@app.route('/checkAgency',methods = ['GET', 'POST'])
def checkAgency():
    form1 = agencyTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('agencyTable.html', form = form1)
                    
        else:
            str_proj = request.form["name"]
            str_man = request.form["manpower"]
            str_equp = request.form["equip"]
            str_travel = request.form["travel"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    cur.execute("select count(*) from agency where name = %s",(str_proj,))
                    n=cur.fetchone()
                    if n[0]==0 :
                            sql = "INSERT INTO agency(name,manpower,equipment,travel) VALUES(%s,%s,%s,%s)"
                            cur.execute(sql,(str_proj,str_man,str_equp,str_travel))
                            conn.commit()
                    else :
                            return ("Name of agency already taken ,please enter other name. Reload to admin page")
                    
                elif(var==3):
                    cur.execute("DELETE FROM agency WHERE name = %s", (str_proj,))
                    conn.commit()

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('agencyTable.html', form = form1)

@app.route('/checkAppH',methods = ['GET', 'POST'])
def checkAppH():
    form1 = appHTable()
    if request.method == 'POST':
        if form1.validate() == False:
            flash('All fields are required.')
            return render_template('appHTable.html', form = form1)
                    
        else:
            strName = request.form["child"]
            strCount = request.form["parent"]
            global var
            conn = None
            try:
                params = config()
                print('Connecting to the PostgreSQL database...')
                conn = psycopg2.connect(**params)
                cur = conn.cursor()
                if(var==1):
                    sql = "INSERT INTO app_hierarchy(child,parent) VALUES(%s,%s)"
                    cur.execute(sql,(strName,strCount))
                elif(var==2):
                    sql = "update app_hierarchy set parent = %s where child = %s"
                    cur.execute(sql,(strCount,strName))
                elif(var==3):
                    cur.execute("DELETE FROM app_hierarchy WHERE child = %s", (strName,))
                    

                else:
                    return render_template('failedIn.html')
                rows_changed = cur.rowcount
                conn.commit()
                cur.close()
                var=0
                if(rows_changed != 0):
                    return render_template('success.html')
                else:
                    return ("No row changed/inserted/deleted, please reload admin page")

            except (Exception, psycopg2.DatabaseError) as error:
                #return render_template('failed.html')
                print(error)
            finally:
                if conn is not None:
                    conn.close()
                    print('Database connection closed.')
            return render_template('failed.html')
            

    elif request.method == 'GET':
        return render_template('appHTable.html', form = form1)




@app.route('/adminLogin',methods = ['GET','POST'])
def adminLogin():
    error=""
    if request.method == 'POST':
        password = request.form["password"]
        if (password != 'team7'):
            error="invalid username or password"
        else:
            return redirect(url_for('admin'))
    return render_template('adminLogin.html', error=error)        

@app.route('/adminLogout',methods = ['GET','POST'])
def adminLogout():
    return redirect(url_for('welcome'))

@app.route('/admin',methods = ['GET', 'POST'])
def admin():
    form = adminWorks()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required.')
            return render_template('adminHome.html', form = form)
        
        else:
            str1 = request.form["Opt"]
            str2 = request.form["Table"]
            global var
            
            if(str2=='fac' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkFaculty'))

            elif(str2=='hod' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkHod'))
                
            elif(str2=='crossC' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkCC'))

            elif(str2=='leaveH' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkLeaveH'))
            
            elif(str2=='proj' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkProj'))

            elif(str2=='copi' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkCopi'))

            elif(str2=='agency' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkAgency'))

            elif(str2=='app_hier' ):
                if(str1=='I'):
                    var=1
                elif(str1=='U'):
                    var=2
                elif(str1=='D'):
                    var=3
                return redirect(url_for('checkAppH'))


            else:
                return "render_template('failed.html') dsa"
            

         
    elif request.method == 'GET':
         return render_template('adminHome.html', form = form)
if __name__ == '__main__':
    global_init()




    
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug = True )

    