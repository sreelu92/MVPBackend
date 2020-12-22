import mariadb
from flask import Flask,request,Response
import json
import dbcreds
from flask_cors import CORS
import secrets
import hashlib
import string
import random
from datetime import date


app= Flask(__name__)

@app.route('/api/users',methods=['GET','POST','PATCH','DELETE'])
def users():
    if request.method=='POST':
        conn=None
        cursor=None
        user_email=request.json.get("email")
        user_username=request.json.get("username")
        user_password=request.json.get("password")
        def createSalt():
            chars=string.ascii_letters+string.digits
            salt=''.join(random.choice(chars) for i in range(10))
            return salt
        salt=createSalt()
        user_password=salt+user_password
        hash_result=hashlib.sha512(user_password.encode()).hexdigest()
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            randomtokens=secrets.token_hex(10)
            if randomtokens:
                cursor.execute("INSERT INTO users(email,password,username,salt) VALUES(?,?,?,?)",[user_email,hash_result,user_username,salt])
                cursor.execute("SELECT * FROM users WHERE username=? AND password=?",[user_username,hash_result])
                infos=cursor.fetchall()
                for info in infos:
                    info[0]
                cursor.execute("INSERT INTO user_session(user_id,login_token) VALUES(?,?)",[info[0],randomtokens])
                conn.commit()
                rows=cursor.rowcount
                userdata={"email":user_email,"username":user_username,"userId":info[0],"loginToken":randomtokens}

        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(userdata,default=str),mimetype="text/html",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

    elif request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        users=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()   
            cursor.execute("SELECT * FROM users WHERE id=?",[userid,])
            users=cursor.fetchall()
            for user in users:
                user[1]
                user[2]
                userdata={"username":user[1],"email":user[2]}
                    
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response(json.dumps(userdata,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

    elif request.method=='PATCH':
        conn=None
        cursor=None
        user_email=request.json.get("email")
        user_username=request.json.get("username")
        user_password=request.json.get("password")
        user_logintoken=request.json.get("loginToken")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if user_logintoken:
                cursor.execute("SELECT u.id,u.salt FROM users u INNER JOIN user_session us ON u.id=us.user_id WHERE us.login_token=?",[user_logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[0],user[1]
            if user_email!="" and user_email!=None:
                cursor.execute("UPDATE users u INNER JOIN user_session us ON u.id=us.user_id SET u.email=? WHERE us.login_Token=? AND u.id=?",[user_email,user_logintoken,user[0]])
            if user_username!="" and user_username!=None:
                cursor.execute("UPDATE users u INNER JOIN user_session us ON u.id=us.user_id SET u.username=? WHERE us.login_Token=? AND u.id=?",[user_username,user_logintoken,user[0]])
            if user_password!="" and user_password!=None:
                user_password=user[1]+user_password
                hash_result=hashlib.sha512(user_password.encode()).hexdigest()
                cursor.execute("UPDATE users u INNER JOIN user_session us ON u.id=us.user_id SET u.password=? WHERE us.login_Token=? AND u.id=?",[hash_result,user_logintoken,user[0]])
            conn.commit()
            rows=cursor.rowcount
            cursor.execute("SELECT u.username,u.email,us.user_id FROM users u INNER JOIN user_session us ON u.id=us.user_id WHERE us.login_token=?",[user_logintoken])
            infos=cursor.fetchall()
            for info in infos:
                info[0],info[1],info[2]
                userdata={"userId":info[2],"username":info[0],"email":info[1]}
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(userdata,default=str),mimetype="application/json",status=200)
            else:
                return Response("Updated failed",mimetype="text/html",status=500)

    elif request.method=='DELETE':
        conn=None
        cursor=None
        rows=None
        user_password=request.json.get("password")
        user_logintoken=request.json.get("loginToken")
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if user_logintoken:
                cursor.execute("SELECT u.password,u.salt FROM users u INNER JOIN user_session us ON u.id=us.user_id WHERE us.login_token=?",[user_logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[0],user[1]
                user_password=user[1] + user_password
                hash_result=hashlib.sha512(user_password.encode()).hexdigest()
                if user[0]==hash_result:
                    cursor.execute("DELETE users,user_session FROM users INNER JOIN user_session ON users.id=user_session.user_id WHERE users.password=? AND user_session.login_token=?",[hash_result,user_logintoken])
                    conn.commit()
                    rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(rows==1):
                return Response("Delete success!",mimetype="text/html",status=204)
            else:
                return Response("Delete failed",mimetype="text/html",status=500)

    



@app.route('/api/login',methods=['POST','DELETE'])
def login():
    if request.method=='POST':
        conn=None
        cursor=None
        user_email=request.json.get("email")
        user_password=request.json.get("password")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            randomtokens=secrets.token_hex(10)   
            if randomtokens:
                cursor.execute("SELECT u.salt FROM users u WHERE u.email=?",[user_email])
                users=cursor.fetchall()
                for user in users:
                    user[0]
                user_password=user[0]+user_password
                hash_result=hashlib.sha512(user_password.encode()).hexdigest()
                if user_email and hash_result:
                    cursor.execute("SELECT * FROM users WHERE email=? AND password=?",[user_email,hash_result])
                    notes=cursor.fetchall()
                    for note in notes:
                        note[0]
                        note[1]
                        note[2]
                        userdata={"userId":note[0],"username":note[1],"email":note[2],"loginToken":randomtokens}
                        cursor.execute("INSERT INTO user_session(user_id,login_token) VALUES(?,?)",[note[0],randomtokens,])
                        conn.commit()
                        rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response(json.dumps(userdata,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

    elif request.method=='DELETE':
        conn=None
        cursor=None
        rows=None
        user_logintoken=request.json.get("loginToken")
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if user_logintoken:
                cursor.execute("SELECT u.id FROM users u INNER JOIN user_session us ON u.id=us.user_id WHERE us.login_token=?",[user_logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[0]
                if user[0]:
                    cursor.execute("DELETE user_session FROM users INNER JOIN user_session ON users.id=user_session.user_id WHERE user_session.login_token=?",[user_logintoken])
                    conn.commit()
                    rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(rows==1):
                return Response("Delete success!",mimetype="text/html",status=204)
            else:
                return Response("Delete failed",mimetype="text/html",status=500)

@app.route('/api/notes',methods=['POST','GET','PATCH','DELETE'])
def  createnotes():
    if request.method=='POST':
        conn=None
        cursor=None
        note_content=request.json.get("content")
        note_logintoken=request.json.get("loginToken")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if note_logintoken:
                cursor.execute("SELECT * FROM user_session WHERE login_token=?",[note_logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[1]
                if note_content:
                    cursor.execute("INSERT INTO notes(content,user_id) VALUES(?,?)",[note_content,user[1]])
                    cursor.execute("SELECT u.username,n.content,n.created_at,n.user_id FROM users u INNER JOIN notes n ON u.id=n.user_id WHERE n.user_id=?",[user[1]])
                infos=cursor.fetchall()
                for info in infos:
                    info[0],info[1],info[2],info[3]
                    notedata={"username":info[0],"content":info[1],"created_at":info[2],"userId":info[3]}
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(notedata,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)


    elif request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        infos=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()   
            if userid:
                cursor.execute("SELECT * FROM notes WHERE user_id=?",[userid])
                infos=cursor.fetchall()
                infoarray=[]
                for info in infos:
                    info[1]
                    info[2]
                    info[3]
                    info[0]
                    infoarray.append({"userId":info[1],"note":info[2],"created_at":info[3],"noteId":info[0]})
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(infoarray,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

    elif request.method=='DELETE':
        conn=None
        cursor=None
        rows=None
        logintoken=request.json.get("loginToken")
        note_id=request.json.get("noteId")
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if logintoken:
                cursor.execute("SELECT * FROM user_session WHERE login_token=?",[logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[1]
                cursor.execute("SELECT * FROM notes WHERE id=?",[note_id])
                newids=cursor.fetchall()
                for newid in newids:
                    newid[1]
                if(user[1]==newid[1]):
                    cursor.execute("DELETE notes FROM notes WHERE id=?",[note_id,])
                    conn.commit()
                    rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response("Delete success!",mimetype="text/html",status=204)
            else:
                return Response("Delete failed",mimetype="text/html",status=500)

    elif request.method=='PATCH':
        conn=None
        cursor=None
        noteid=request.json.get("noteId")
        logintoken=request.json.get("loginToken")
        content=request.json.get("content")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if logintoken:
                if content!="" and content!=None:
                    cursor.execute("UPDATE notes n INNER JOIN user_session us ON n.user_id=us.user_id SET n.content=? WHERE n.id=? AND us.login_token=?",[content,noteid,logintoken])
            conn.commit()
            rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(rows==1):
                return Response("Updated success!",mimetype="text/html",status=200)
            else:
                return Response("Updated failed",mimetype="text/html",status=500)

@app.route('/api/ordernotes',methods=['GET'])
def orderingNotes():
    if request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        infos=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()   
            if userid:
                cursor.execute("SELECT * FROM user_session WHERE user_id=?",[userid])
                users=cursor.fetchall()
                for user in users:
                    user[2]
                cursor.execute("SELECT n.content,n.id FROM notes n INNER JOIN user_session us ON n.user_id=us.user_id  WHERE us.login_token=? ORDER BY created_at ASC",[user[2]])
                infos=cursor.fetchall()
                infoarray=[]
                for info in infos:
                    info[0]
                    infoarray.append({"note":info[0],"noteId":info[1]})
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(infoarray,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

@app.route('/api/tasks',methods=['GET','POST','PATCH','DELETE'])
def createTask():
    if request.method=='POST':
        conn=None
        cursor=None
        task_content=request.json.get("content")
        task_logintoken=request.json.get("loginToken")
        task_date=request.json.get("date")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if task_logintoken:
                cursor.execute("SELECT * FROM user_session WHERE login_token=?",[task_logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[1]
                if task_content:
                    cursor.execute("INSERT INTO task(content,user_id,complete_date) VALUES(?,?,?)",[task_content,user[1],task_date])
                    cursor.execute("SELECT u.username,t.content,t.created_at,t.user_id,t.complete_date FROM users u INNER JOIN task t ON u.id=t.user_id WHERE t.user_id=?",[user[1]])
                    infos=cursor.fetchall()
                for info in infos:
                    info[0],info[1],info[2],info[3],info[4]
                    taskdata={"username":info[0],"content":info[1],"created_at":info[2],"userId":info[3],"Target_date":info[4]}
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response(json.dumps(taskdata,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)
    
    elif request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        infos=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()   
            if userid:
                cursor.execute("SELECT * FROM task WHERE user_id=?",[userid])
                infos=cursor.fetchall()
                infoarray=[]
                for info in infos:
                    info[1]
                    info[2]
                    info[3]
                    info[0]
                    info[4]
                    infoarray.append({"userId":info[1],"task":info[2],"created_at":info[3],"taskId":info[0],"targetDate":info[4]})
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(infoarray,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

    elif request.method=='PATCH':
        conn=None
        cursor=None
        taskid=request.json.get("taskId")
        logintoken=request.json.get("loginToken")
        content=request.json.get("content")
        taskdate=request.json.get("date")
        rows=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if logintoken:
                if content!="" and content!=None:
                    cursor.execute("UPDATE task t INNER JOIN user_session us ON t.user_id=us.user_id SET t.content=? WHERE t.id=? AND us.login_token=?",[content,taskid,logintoken])
                if taskdate!="" and taskdate!=None:
                    cursor.execute("UPDATE task t INNER JOIN user_session us ON t.user_id=us.user_id SET t.complete_date=? WHERE t.id=? AND us.login_token=?",[taskdate,taskid,logintoken])
                conn.commit()
                rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(rows==1):
                return Response("Updated success!",mimetype="text/html",status=200)
            else:
                return Response("Updated failed",mimetype="text/html",status=500)
    elif request.method=='DELETE':
        conn=None
        cursor=None
        rows=None
        logintoken=request.json.get("loginToken")
        taskid=request.json.get("taskId")
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()
            if logintoken:
                cursor.execute("SELECT * FROM user_session WHERE login_token=?",[logintoken])
                users=cursor.fetchall()
                for user in users:
                    user[1]
                cursor.execute("SELECT * FROM task WHERE id=?",[taskid])
                newids=cursor.fetchall()
                for newid in newids:
                    newid[1]
                if(user[1]==newid[1]):
                    cursor.execute("DELETE task FROM task WHERE id=?",[taskid,])
                    conn.commit()
                    rows=cursor.rowcount
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response("Delete success!",mimetype="text/html",status=204)
            else:
                return Response("Delete failed",mimetype="text/html",status=500)

@app.route('/api/ordertasks',methods=['GET'])
def orderingTasks():
    if request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        infos=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor()   
            if userid:
                cursor.execute("SELECT * FROM user_session WHERE user_id=?",[userid])
                users=cursor.fetchall()
                for user in users:
                    user[2]
                cursor.execute("SELECT t.content,t.complete_date,t.id FROM task t INNER JOIN user_session us ON t.user_id=us.user_id  WHERE us.login_token=? ORDER BY complete_date ASC",[user[2]])
                infos=cursor.fetchall()
                infoarray=[]
                for info in infos:
                    info[0],info[1],info[2]
                    infoarray.append({"task":info[0],"targetDate":info[1],"taskId":info[2]})
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(infos!=None):
                return Response(json.dumps(infoarray,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)

@app.route('/api/daytasks',methods=['GET'])
def todaysTasks():
    if request.method=='GET':
        conn=None
        cursor=None
        userid=request.args.get("userId")
        infos=None
        try:
            conn=mariadb.connect(user=dbcreds.user, password=dbcreds.password, host=dbcreds.host, port=dbcreds.port, database=dbcreds.database)
            cursor=conn.cursor() 
            today=date.today()  
            cursor.execute("SELECT * FROM user_session WHERE user_id=?",[userid])
            users=cursor.fetchall()
            for user in users:
                user[2]
            cursor.execute("SELECT t.id,t.content,t.complete_date FROM task t INNER JOIN user_session us WHERE t.complete_date=? AND us.login_token=? AND t.user_id=?",[today,user[2],userid])
            infos =cursor.fetchall()
            infoarray=[]

            for info in infos :
                info[0],info[1],info[2]
                infoarray.append({"taskId":info[0],"task":info[1],"targetDate":info[2]})
                    
           
        except mariadb.ProgrammingError as error:
            print("Something went wrong with coding ")
            print(error)
        except mariadb.DatabaseError as error:
            print("There is a database error")
            print(error)
        except mariadb.OperationalError as error:
            print("Connection error occured. Please try again later!")
        finally:
            if(cursor!=None):
                cursor.close()
            if(conn!=None):
                conn.rollback()
                conn.close()
            if(users!=None):
                return Response(json.dumps(infoarray,default=str),mimetype="application/json",status=200)
            else:
                return Response("Something went wrong",mimetype="text/html",status=500)











