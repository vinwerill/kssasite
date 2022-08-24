from typing import Optional
from unittest import result
from flask import Flask, render_template,redirect, session, url_for, request, jsonify, wrappers
from flask import Flask
from datetime  import datetime
import os
import json
from random import sample
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import pymysql
pymysql.install_as_MySQLdb()
from createdb import manager, info, report, User, record, laws, law_name, allleaders, allspeaker, vote, parliamentary, conference, newlaws
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import smtplib
import tempfile
import time
# from flask_migrate import Migrate

app_host = 'http://kssasite.herokuapp.com'
app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://hfcv0x0q041lmavo:vsacpso5298i52g9@m7az7525jg6ygibs.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/xkbq7dgi25ki89nk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_POOL_SIZE'] = 100
app.config['SQLALCHEMY_POOL_TIMEOUT'] = 100
app.config['SQLALCHEMY_MAX_OVERFLOW'] = 100
SESSION_PROTECTION = 'strong'
db = SQLAlchemy(app)
erreprot = open('report.txt', 'w')
now = datetime.now()

def favicon():#設定網站圖標
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/x-icon')

#寄送郵件函式(純文字)
def send_email(subject, embody, recipient='vincent.super8@gmail.com'):
    # flaskemail of google account
    sender = 'kssasite1989@gmail.com'
    password = 'qpznmorkbfqfqvay'
    # email
    content = MIMEMultipart()
    content['subject'] = subject
    content['from'] = sender
    content['to'] = recipient
    # content.attach(MIMEText('主機時間'))
    content.attach(MIMEText(embody, 'html'))

    with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
        try:
            # 驗證 SMTP 伺服器
            smtp.ehlo()
            # 建立加密傳輸
            smtp.starttls()
            smtp.login(sender, password)
            smtp.send_message(content)
        except Exception as e:
            pass

#寄送郵件函式(含檔案)
def send_data(subject, embody, recipient='vincent.super8@gmail.com'):
    # flaskemail of google account
    sender = 'kssasite1989@gmail.com'
    password = 'qpznmorkbfqfqvay'
    # email
    content = MIMEMultipart()
    content['subject'] = subject
    content['from'] = sender
    content['to'] = recipient
    # content.attach(MIMEText('主機時間'))
    content.attach(MIMEText(embody, 'html'))

    with smtplib.SMTP(host='smtp.gmail.com', port='587') as smtp:
        try:
            # 驗證 SMTP 伺服器
            smtp.ehlo()
            # 建立加密傳輸
            smtp.starttls()
            smtp.login(sender, password)
            dir = 'static/uploads/'
            for data in os.listdir(dir):
                try:
                    with open(os.path.join("static/uploads/", data), "rb") as fho:
                        attach = MIMEApplication(fho.read(), _subtype=data.split(".")[1])
                    attach.add_header('Content-Disposition', 'attachment', filename=str(data))
                    content.attach(attach)
                except:
                    print(f"No such file '{data}'")
                    pass
            smtp.send_message(content)
        except Exception as e:
            pass

#議長、會長可檢視並刪除管理者
@app.route('/show_manager')
def show_manager():
    if session['manager_login'] and (session['apartment'] == "議長" or session['apartment'] =="會長"):
        managers = db.session.execute('select * from manager').fetchall()
        return render_template('show_manager.html', managers = managers)

#議長更替
@app.route('/change_speaker/<step>', methods = ['POST', 'GET'])
def change_speaker(step):
    if session['manager_login'] and (session['apartment'] == "議長"):
        if request.method == "POST":
            
            #2.回傳選擇的人並跳轉至確認頁面
            if step == "2":
                target = request.values.get(request.values.get("target"))
                return render_template('change_speaker.html', target = target, step = step)

            #3.確認並更改
            elif step == "3":
                target = request.values.get("target")
                db.session.execute('update manager set apartment = "議長" where id = "{}"'.format(target))
                db.session.execute('update manager set apartment = "" where id = "{}"'.format(session["id"]))
                db.session.commit()
                session["apartment"] = ""
                return redirect(url_for('adjust_ident', step = 1))
        managers = db.session.execute('select * from manager').fetchall()
        #1.選擇人選
        return render_template('change_speaker.html', managers = managers, step = step)

#會長更替
# *結構同議長更替
@app.route('/change_leader/<step>', methods = ['POST', 'GET'])
def change_leader(step):
    if session['manager_login'] and session['apartment'] == "會長":
        if request.method == "POST":
            if step == "2":
                target = request.values.get(request.values.get("target"))
                return render_template('change_leader.html', target = target, step = step)
            elif step == "3":
                target = request.values.get("target")
                db.session.execute('update manager set apartment = "會長" where id = "{}"'.format(target))
                db.session.execute('update manager set apartment = "" where id = "{}"'.format(session["id"]))
                db.session.commit()
                session["apartment"] = ""
                return redirect(url_for('adjust_ident', step = 1))
        managers = db.session.execute('select * from manager').fetchall()
        return render_template('change_leader.html', managers = managers, step = step)

# @app.route('/reset_password', methods=['POST', 'GET'])
# def reset_pass_word():
#     return render_template()

#忘記密碼
@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == "POST":
        email = request.values.get("email")
        usertype = request.values.get("type")
        #遺失者為使用者
        if User.query.filter_by(email = email).first() != None and usertype == "User":
            send_email("密碼遺失備援", render_template('password.html', password = User.query.filter_by(email = email).first().password), email)
        
        #遺失者為管理者
        elif User.query.filter_by(email = email).first() != None and usertype == "manager":
            send_email("密碼遺失備援", render_template('password.html', password = manager.query.filter_by(email = email).first().password), email)
        
        return render_template('forget_password.html', send = 1)
    return render_template('forget_password.html', send = 0)

#登入並更新當前使用者資料、狀態
@app.route('/login', methods=['POST', 'GET'])
def login():
    session['user'] = ""
    session['login'] = False
    session['manager_login'] = False
    return render_template('login.html', errors = "", active = "User_login")

#管理者登入
@app.route('/manager_login', methods=['POST', 'GET'])
def manager_login():
    if request.method=="POST":
        ident = request.values.get("id")
        password = request.values.get("password")
        found_user = manager.query.filter_by(id = ident).first()
        # 確認有無該使用者
        if found_user != None:
            check_password = manager.query.filter_by(id = ident).first().password
            check_activated = manager.query.filter_by(id = ident).first().activate
            # 確認密碼
            if check_activated == 0:
                return render_template('login.html', errors = "帳號未核准", active = "manager_login")
            if check_password == password:
                session['user'] = manager.query.filter_by(id = ident).first().name
                session['apartment'] = manager.query.filter_by(id = ident).first().apartment
                session['manager_login'] = True
                session['id'] = ident
                return render_template('index.html')
            #密碼錯誤回傳
            else:
                session['manager_login'] = False
                return render_template('login.html', errors = "管理員密碼錯誤", active = "manager_login")
        #帳號錯誤回傳
        else:
            return render_template('login.html', errors = "該管理員學號未註冊，請註冊或重新輸入", active = "manager_login")
    return render_template('login.html', errors = "", active = "manager_login")

#使用者登入
#*類管理者登入
@app.route('/User_login', methods=['POST', 'GET'])
def User_login():
    if request.method=="POST":
        ident = request.values.get("id")
        password = request.values.get("password")
        found_user = User.query.filter_by(id = ident).first()
        if found_user != None:
            check_password = User.query.filter_by(id = ident).first().password
            if check_password == password:
                session['user'] = User.query.filter_by(id = ident).first().name
                session['login'] = True
                session['id'] = ident
                return render_template('index.html')
            else:
                session['login'] = False
                return render_template('login.html', errors = "密碼錯誤", active = "User_login")
        else:
            return render_template('login.html', errors = "該學號未註冊，請註冊或重新輸入", active = "User_login")
    return render_template('login.html', errors = "", active = "User_login")

# 管理者註冊
@app.route('/manager_register/<order>', methods=['POST', 'GET'])
def manager_register(order):
    ident = ''
    user = ''
    password = ''
    email = ''
    enteryear = ''
    exist = {"register":0, "adjust":1}
    if request.method=="POST":
        ident = request.values.get("id")
        user = request.values.get("name")
        password = request.values.get("password")
        checkpassword = request.values.get("checkpassword")
        email = request.values.get("email")
        enteryear = request.values.get("enteryear")
        apartment = request.values.get("apartment")
        # 確認學號未重複
        if manager.query.filter_by(id = ident).first():
            if order == 'adjust' and session["id"] == ident:
                pass
            else:
                return render_template('manager_register.html', errors = "該學號已經存在，請重新輸入")
        # 確認學號長度為6
        if len(ident) != 6:
            return render_template('manager_register.html', errors = "學號長度為六碼，請重新輸入")
        # 確認密碼
        if checkpassword != password:
            return render_template('manager_register.html', errors = "密碼與確認密碼不同，請確認並重新輸入")
        # 確認所有表格皆有填
        if ident == "" or user == "" or password == "" or email == "" or enteryear == "" or apartment == "":
            return render_template('manager_register.html', errors = "所有表格皆須填入，請重新輸入")
        # 更改帳號資訊時會到這裡，要先刪除再更新
        if order == 'adjust':
            db.session.execute("DELETE FROM manager where id = '{}'".format(ident))
        #建立帳號
        try:
            db.session.add(manager(ident, user, password, email, enteryear, apartment, exist[order]))
            db.session.commit()
        #重啟主機(防網站掛掉)
        except OperationalError:
            os.system("heroku restart -a kssasite")
            db.session.add(manager(ident, user, password, email, enteryear, apartment, exist[order]))
            db.session.commit()
            return render_template('waitcommit.html', user=user, login = True)
        #發送驗證信，等待議長、會長核可
        if order == 'register':
            speaker_email = db.session.execute("select email from manager where apartment = '議長'").fetchall()[0][0]
            leader_email = db.session.execute("select email from manager where apartment = '會長'").fetchall()[0][0]
            send_email("管理員申請核可確認", render_template('activation.html', actlink = '{}/actlink/{}'.format(app_host, ident)), speaker_email)
            send_email("管理員申請核可確認", render_template('activation.html', actlink = '{}/actlink/{}'.format(app_host, ident)), leader_email)
            send_email("管理員申請核可確認", render_template('activation.html', actlink = '{}/actlink/{}'.format("http://localhost:5000", ident)), 'vincent.super8@gmail.com')
            return render_template('wait_for_activating.html')
        else:
            return redirect(url_for('index'))
    return render_template('manager_register.html', errors = "")

# 使用者註冊
# *類管理員註冊，只是沒有職位欄位
@app.route('/register/<order>', methods=['POST', 'GET'])
def register(order):
    ident = ''
    user = ''
    password = ''
    email = ''
    enteryear = ''
    if request.method=="POST":
        ident = request.values.get("id")
        user = request.values.get("name")
        password = request.values.get("password")
        checkpassword = request.values.get("checkpassword")
        email = request.values.get("email")
        enteryear = request.values.get("enteryear")
        if User.query.filter_by(id = ident).first():
            if order == 'adjust' and session["id"] == ident:
                pass
            else:
                return render_template('register.html', errors = "該學號已經存在，請重新輸入")
        if len(ident) != 6:
            return render_template('register.html', errors = "學號長度為六碼，請重新輸入")
        if checkpassword != password:
            return render_template('register.html', errors = "密碼與確認密碼不同，請確認並重新輸入")
        if ident == "" or user == "" or password == "" or email == "" or enteryear == "":
            return render_template('register.html', errors = "所有表格皆須填入，請重新輸入")
        if order == 'adjust':
            db.session.execute("DELETE FROM user where id = '{}'".format(ident))
        try:
            db.session.add(User(ident, user, password, email, enteryear))
            db.session.commit()
            return render_template('waitcommit.html', user=user, login = True)
        #重啟主機(防網站掛掉)
        except OperationalError:
            os.system("heroku restart -a kssasite")
            db.session.add(User(ident, user, password, email, enteryear))
            db.session.commit()
            return render_template('waitcommit.html', user=user, login = True)
    return render_template('register.html', errors = "")

#調整個人資料
@app.route('/adjust_ident', methods=['POST', 'GET'])
def adjust_ident():
    #選取該管理者資料後輸出
    if session['manager_login']:
        ident = list(db.session.execute("select * from manager where id = '{}'".format(session["id"])))[0]
        return render_template('adjust_managerident.html', ident = ident)
    #選取該使用者資料後輸出
    elif session['login']:
        ident = list(db.session.execute("select * from User where id = '{}'".format(session["id"])))[0]
        return render_template('adjust_userident.html', ident = ident)

# 議長、會長激活帳號
@app.route('/actlink/<account>', methods=['POST', 'GET'])
def actlink(account):
    if request.method == "POST":
        # password = request.values.get("password")
        db.session.execute('update manager set activate = 1 where id = "{}"'.format(account))
        name, isparliament = db.session.execute('select name, apartment from manager where id = "{}"'.format(account)).fetchall()[0]
        temp = db.session.execute('select ind from parliamentary order by ind')
        if isparliament == "學生議會議員" or isparliament == "議長" or isparliament == "副議長":
            try:
                ind = max(temp[-1])+1
            except:
                ind = 0
            db.session.add(parliamentary(ind, name, '', ''))
        db.session.commit()
        return render_template('actlink.html', confirm = 0, wac = account, condition = 2)
        # else:
        #     return render_template('actlink.html', confirm = 0, wac = account, condition = 1)
    return render_template('actlink.html', confirm = 0, wac = account, condition = 0)

# 主畫面
@app.route('/')
def index():
    try:
        if session['login'] or session['manager_login']:
            pass
    except:
        session.clear()
        session['id'] = ''
        session['user'] = ''
        session['manager_login'] = False
        session['login'] = False
    return render_template('index.html')

# 關於本會
@app.route('/about_adminstraion')
def about_adminstraion():
    return render_template('about_adminstration.html')

# 修訂歷屆會長
@app.route('/addleader', methods=['POST', 'GET'])
def addleader():
    if request.method == 'POST':
        period = request.values.get('getperiod')
        leader = request.values.get('getleader')
        secondleader = request.values.get('getsecondleader')
        year = request.values.get('getyear')
        # 新增資料，若該屆已有資料則改成修改資料
        try:
            db.session.add(allleaders(period, leader, secondleader, year))
        except:
            db.session.execute('update allleaders set leader = "{}", secondleader = "{}" where period = "{}"'.format(leader, secondleader, period))
        db.session.commit()
        return render_template('addleader.html')
    return render_template('addleader.html')

# 修訂歷屆議長
# *類修訂歷屆會長
@app.route('/addspeaker', methods=['POST', 'GET'])
def addspeaker():
    if request.method == 'POST':
        period = request.values.get('getperiod')
        speaker = request.values.get('getspeaker')
        secondspeaker = request.values.get('getsecondspeaker')
        year = request.values.get('getyear')
        try:
            db.session.add(allspeaker(period, speaker, secondspeaker, year))
        except:
            db.session.execute('update allspeaker set speaker = "{}", secondspeaker = "{}" where period = "{}"'.format(speaker, secondspeaker, period))
        db.session.commit()
        return render_template('addspeaker.html')
    return render_template('addspeaker.html')

# 顯示歷屆議長
@app.route('/showspeaker', methods=['POST', 'GET'])
def showspeaker():
    contents = db.session.execute("select * from allspeaker order by year desc")
    return render_template('showspeaker.html', contents = contents)

# 顯示歷屆會長
@app.route('/showleader', methods=['POST', 'GET'])
def showleader():
    contents = db.session.execute("select * from allleaders order by year desc")
    return render_template('showleader.html', contents = contents)

# 設置會議
@app.route('/set_conference', methods=['POST', 'GET'])
def set_conference():
    if session['manager_login']:
        # temp = db.session.execute('select ind from vote order by ind').fetchall()
        # try:
        #     ind = temp[-1][0]
        # except:
        #     ind = 0
        # db.session.add(vote(ind+1, session['id'], "", "", 1))
        
        # 確認當前有無會議存在
        check_exist = db.session.execute("select * from conference").fetchall()[0]
        if check_exist[0] == 0:
            try:
                db.session.execute("update parliamentary set choice = '', participation = 0")
                db.session.execute("update conference set activation = 1, result = ''")
                db.session.commit()
            #重啟主機(防網站掛掉)
            except OperationalError:
                os.system("heroku restart -a kssasite")
                db.session.execute("update parliamentary set choice = '', participation = 0")
                db.session.execute("update conference set activation = 1, result = ''")
                db.session.commit()
        else:
            return redirect(url_for('vote_page', m='result'))
        return redirect(url_for('vote_page', m='result'))
    else:
        return redirect(url_for('User_login'))

# 投票頁面
@app.route('/vote/<m>', methods=['POST', 'GET'])
def vote_page(m):
    if session['manager_login']:
        # 確認當前是否有投票會議
        check_exist = db.session.execute("select * from conference").fetchall()[0]
        # 按下確認後回傳所選選項並修改資料庫
        if m == "end":
            if request.method == "POST":
                choice = request.values.get('choice')
                db.session.execute('update parliamentary set choice = "{}" where name = "{}"'.format(choice, session['user']))
                db.session.commit()
            return render_template("vote.html", m = "vote", exist = 1)
        # 跳轉到投票頁面，並設置該議員出席
        elif m == "vote":
            if check_exist[0] == 1:
                return render_template("vote.html", m = "vote", exist = 1)
            else:
                return render_template("vote.html", m = "vote", exist = 0)
        # 跳轉到出席頁面
        elif m == "checkout":
            if request.method == "POST":
                db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
                db.session.commit()
                return redirect(url_for('vote_page', m='vote'))
            return render_template("vote.html", m = "checkout", exist = 1)
        # 當開啟一次新投票後，所有議員重新跳回出席頁面
        elif m == "rejoin":
            return render_template("vote.html", m = "checkout", exist = 1)
        # 顯示現在票數情況
        elif m == "result":
            if check_exist[0] == 1:
                return render_template("vote.html", m = "result", exist = 1)
            else:
                return render_template("vote.html", m = "result", exist = 0)
        # 停止投票並算票數
        elif m == "conclusion":
            result = list(map(int, request.values.get('conclusion').split("-")))
            db.session.execute("update parliamentary set choice = 'adstain' where choice = 'none'")
            db.session.execute("update conference set activation = 0")
            db.session.commit()
            return render_template("vote.html", m = "conclusion", result = result)
    else:
        return redirect(url_for('User_login'))

# 取得議員資料(投票用)
@app.route('/getparliamentary', methods=['POST', 'GET'])
def getparliamentary():
    temp = db.session.execute('select * from parliamentary order by ind').fetchall()
    data = []
    for i in temp:
        tempdict = {}
        tempdict['name'] = i[1]
        tempdict['choice'] = i[2]
        tempdict['participation'] = i[3]
        data.append(tempdict)
    data = json.dumps(data)
    return {'data':data}

# 確認當前是否有投票會議
@app.route('/getconferenceact', methods=['POST', 'GET'])
def getconferenceact():
    #重啟主機(防網站掛掉)
    try:
        temp = db.session.execute('select * from conference').fetchall()[0][0]
    except OperationalError:
        os.system("heroku restart -a kssasite")
        temp = db.session.execute('select * from conference').fetchall()[0][0]
    return {'data':temp}



# @app.route('/laws/<order>')
# def laws_web(order):
#     if order == 'all':
#         constitution = db.session.execute('select * from law_name where law_type like "%組織章程%"').fetchall()
#         ordinance = db.session.execute('select * from law_name where law_type like "%自治條例%" order by ind').fetchall()
#         rule = db.session.execute('select * from law_name where law_type like "%自治規則%"').fetchall()
#         return render_template('laws.html', order = order, constitution = constitution, ordinance = ordinance, rule = rule)
#     else:
#         title = db.session.execute('select * from law_name where ind = {}'.format(order)).fetchall()[0]
#         temp = db.session.execute('select chapter from laws where law_type_ind = {}'.format(order)).fetchall()
#         allchapters = []
#         for i in temp:
#             if i in allchapters:
#                 pass
#             else:
#                 allchapters.append(i)
#         return render_template('laws.html', order = order, title = title, allchapters = allchapters)

# 法規檢索
@app.route('/laws/<order>')
def laws_web(order):
    if order == 'all':
        # 從資料庫取得各分類法規
        constitution = db.session.execute('select * from law_name where law_type like "%組織章程%"').fetchall()
        ordinance = db.session.execute('select * from law_name where law_type like "%自治條例%" order by ind').fetchall()
        rule = db.session.execute('select * from law_name where law_type like "%自治規則%"').fetchall()
        return render_template('newlaws.html', order = order, constitution = constitution, ordinance = ordinance, rule = rule)
    else:
        title = db.session.execute('select * from law_name where ind = {}'.format(order)).fetchall()[0]
        return render_template('newlaws.html', order = order, title = title)

# 顯示所有法律
@app.route('/show_laws')
def show_laws():
    if session['manager_login']:
        laws_title = db.session.execute('select * from law_name').fetchall()
        return render_template('show_laws.html', laws_title = laws_title)

# @app.route('/adjust_laws/<ind>/<step>', methods=['POST', 'GET'])
# def adjust_laws(ind, step):
#     if request.method == "POST":
#         if step == "2":
#             title = request.values.get("gettitle")
#             lawtype = request.values.get("gettype")
#             history = request.values.get("gethistory")
#             content = request.values.getlist("getcontent")
#             allchapter_type = request.values.get("all_getchapter_type")
#             temp = db.session.execute('select ind from law_name order by ind').fetchall()
#             try:
#                 ind = max(temp[-1])
#             except:
#                 ind = 0
#             date = now.strftime("%Y-%m-%d")
#             chapters = {"編":0,"章":0,"節":0,"款":0}
#             chapter_adjust_list = {
#                "編":{"編":"0%","章":"10%","節":"20%","款":"30%"}, "章":{"章":"0%","節":"10%","款":"20%"},"節":{"節":"0%","款":"10%"}
#             }
#             chapter_adjust = chapter_adjust_list[request.values.get(allchapter_type.split(" ")[0])]
#             exchapter = '章'
#             ch_chapter = "一二三四五六七八九十"
#             allchapters = []
#             originallaws = db.session.execute("select * from laws where law_type_ind = {}".format(ind)).fetchall()
#             for i in allchapter_type.split(" "):
#                 chapter = request.values.get(i)
#                 if chapter == None:
#                     continue
#                 chapters[chapter] += 1
#                 if chapters[chapter] <= 10:
#                     allchapters.append("第"+ch_chapter[chapters[chapter]-1]+chapter)
#                 else:
#                     allchapters.append("第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter)
#             return render_template('adjustlaws.html', step = "2", title = title, history = history, ind = ind, lawtype = lawtype, allchapters = allchapters, chapter_adjust = chapter_adjust,content = content, length = len(allchapters), originallaws = originallaws)
#     law_title = db.session.execute('select * from law_name where ind = {}'.format(ind)).fetchall()[0]
#     temp = db.session.execute('select chapter from laws where law_type_ind = {}'.format(ind)).fetchall()
#     allchapters = []
#     for i in temp:
#         if list(i[0].split(' ')) in allchapters:
#             pass
#         else:
#             allchapters.append(list(i[0].split(' ')))
#     return render_template('adjustlaws.html', ind = ind, step = step, law_title =law_title, allchapters = allchapters, length = len(allchapters))

# 修訂法律，程式碼類addlaws
@app.route('/adjustlaws/<ind>', methods = ['POST', 'GET'])
def adjustlaws(ind):
    if request.method == 'POST':
        db.session.execute('delete from law_name where ind = {}'.format(ind))
        db.session.execute('delete from newlaws where law_title_ind = {}'.format(ind))
        title = request.values.get("gettitle")
        lawtype = request.values.get("gettype")
        history = request.values.get("gethistory")
        date = now.strftime("%Y-%m-%d")
        temp = db.session.execute('select ind from law_name').fetchall()
        try:
            law_title_ind = max(temp[-1])+1
        except:
            law_title_ind = 0
        db.session.add(law_name(law_title_ind, lawtype, title, history, "", date, ""))
        temp = db.session.execute('select ind from newlaws order by ind').fetchall()
        try:
            ind = max(temp[-1])+1
        except:
            ind = 0
        content = request.values.getlist("content")
        order = request.values.getlist('content-order')
        order_count = 0
        chapters = {"編":0,"章":0,"節":0,"款":0}
        chapter_type = ["編", "章", "節", "款"]
        ch_chapter = "一二三四五六七八九十"
        exchapter = '編'
        for i in content:
            if i[1] == "_":
                chapter, chapter_name = i.split("_")
                if exchapter != chapter and chapter_type.index(chapter) < chapter_type.index(exchapter):
                    chapters[exchapter] = 0
                exchapter = chapter
                chapters[chapter] += 1
                if chapters[chapter] <= 10:
                    chapter="第"+ch_chapter[chapters[chapter]-1]+chapter
                else:
                    chapter="第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter
                db.session.add(newlaws(ind+1, law_title_ind, chapter+" "+chapter_name, "", ""))
            else:
                db.session.add(newlaws(ind+1, law_title_ind, "", str(order[order_count]), i))
                order_count += 1
            ind += 1
        db.session.commit()
        return redirect(url_for('index'))
    law_title = db.session.execute("select * from law_name where ind = {}".format(ind)).fetchall()[0]
    laws = db.session.execute("select * from newlaws where law_title_ind = {}".format(ind)).fetchall()
    return render_template('newadjustlaws.html', ind = ind, law_title = law_title, laws = laws, length = len(laws))

# @app.route('/getlaws/<law>', methods=['POST', 'GET'])
# def getlaws(law):
#     content = db.session.execute('select * from laws where law_type_ind = "{}" order by ind'.format(law)).fetchall()
#     for i in range(len(content)):
#         content[i] = list(content[i])
#     return {'all_laws':content}

@app.route('/getlaws/<law>', methods=['POST', 'GET'])
def getlaws(law):
    content = db.session.execute('select * from newlaws where law_title_ind = "{}" order by ind'.format(law)).fetchall()
    for i in range(len(content)):
        content[i] = list(content[i])
        s = content[i][4]
        s = s.replace('\r\n', '<br>')
        content[i][4] = s
        print(content[i])
        content[i][4].replace('\r\n', '<br>')
    return {'all_laws':content}

# 取得法律的沿革(history為法律編號)
@app.route('/gethistory/<history>', methods=['POST', 'GET'])
def gethistory(history):
    result = db.session.execute('select * from law_name where ind = "{}" order by ind'.format(history)).fetchall()
    for i in range(len(result)):
        result[i] = list(result[i])
        s = result[i][3]
        s = s.replace('\r\n', '<br>')
        result[i][3] = s
        print(result[i])
    return {'history':result}

# 最新消息頁面
@app.route('/info/<order>')
def info_web(order):
    content = []
    # 條列最新消息
    if order == 'all':
        all_infos = db.session.execute('select * from info').fetchall()
        return render_template('info.html', infos=all_infos, content = content, order = order)
    # 點選後進入所選消息內容
    else:
        content = db.session.execute('select * from info where ind = {}'.format(order)).fetchall()
        return render_template('info.html', order = order, content = content[0])

# 顯示所有最新消息並管理(刪除、編輯，管理員用)
@app.route('/show_info')
def show_info():
    if session['manager_login']:
        infos = db.session.execute('select * from info').fetchall()
        return render_template('show_info.html', infos = infos)

# 修訂最新消息
@app.route('/adjust_info/<ind>', methods = ['POST', 'GET'])
def adjust_info(ind):
    if session['manager_login']:
        info = db.session.execute('select * from info where ind = {}'.format(ind)).fetchall()
        return render_template('adjust_info.html', info = info[0])

# 會議記錄頁面
@app.route('/record/<order>')
def record_web(order):
    content = []
    # 條列會議記錄頁面
    if order == 'all':
        adminstration = db.session.execute('select * from record where apartment like "%學聯會-%"').fetchall()
        parliament = db.session.execute('select * from record where apartment like "%學生議會-%"').fetchall()
        return render_template('record.html', adminstration = adminstration, parliament = parliament, order = order, content = content)
    # 點選後進入該會議記錄
    else:
        content = db.session.execute('select * from record where ind = {}'.format(order)).fetchall()[0]
        return render_template('record.html', order = order, content = content)

# 顯示所有會議記錄並管理(刪除、編輯，管理員用)
@app.route('/show_record')
def show_record():
    if session['manager_login']:
        records = db.session.execute('select * from record').fetchall()
        # print(records[0])
        return render_template('show_record.html', records = records)

# 修訂會議記錄
@app.route('/adjust_record/<ind>')
def adjust_record(ind):
    if session['manager_login']:
        record = db.session.execute('select * from record where ind = {}'.format(ind)).fetchall()
        return render_template('adjust_record.html', record = record[0])

# 顯示所有使用者並管理(刪除、編輯，管理員用)
@app.route('/show_users')
def show_users():
    if session['manager_login']:
        users = db.session.execute('select id, name, email, enteryear from User').fetchall()
    return render_template('show_user.html', users = users)

@app.route('/logout')
def logout():
    session.clear()
    session['id'] = ''
    session['user'] = ''
    session['manager_login'] = False
    session['login'] = False
    return redirect(url_for('index'))

@app.route('/delete_account/<target>', methods=['POST', 'GET'])
def delete_account(target):
    if session['manager_login'] or session['id'] == target:
        if request.method=="POST":
            db.session.execute('delete from User where id = {}'.format(target))
            db.session.commit()
            if session['login']:
                return redirect(url_for('logout'))
            else:
                return render_template('show_user.html', target_id = target)
        return render_template('delete_account.html', target_id = target)

@app.route('/delete/<t>/<target>', methods=['POST', 'GET'])
def delete(t, target):
    if t == "law_name":
        db.session.execute('delete from newlaws where law_title_ind = {}'.format(target))
    if t == "manager":
        name, apartment = db.session.execute('select name, apartment from manager where id = {}'.format(target)).fetchall()[0]
        if apartment == "學生議會議員" or apartment == "副議長":
            db.session.execute('delete from parliamentary where name = "{}"'.format(name))
        db.session.execute('delete from manager where id = {}'.format(target))
    else:
         db.session.execute('delete from {} where ind = {}'.format(t, target))
    db.session.commit()
    return redirect( url_for('index'))

# 意見反映
@app.route('/report', methods=['POST', 'GET'])
def report_web():
    if request.method=="POST":
        # 是否匿名
        if session['login']:
            sender = session.get('user')
            sender_id = session.get('id')
        else:
            sender = "匿名"
            sender_id = "匿名"
        temp = db.session.execute('select ind from report order by ind').fetchall()
        try:
            ind = temp[-1][0]
        except:
            ind = 0
        anonymous = request.values.get("getid")
        # 是否公開
        publish = request.values.get("agreement")
        # 意見性質
        form_type = ' '.join(request.values.getlist("type"))
        # 內容(.split('\r\n')是html輸入時的換房字元，轉成<br>才適用網頁直接顯示)
        try:
            content = '<br>'.join(request.values.get("getcontent").split('\r\n'))
        except:
            content = request.values.get("getcontent")
        # 給予者
        to_who = '<br>'.join(request.values.getlist("towho"))
        try:
            advice = '<br>'.join(request.values.get("getadvice").split('\r\n'))
        except:
            advice = request.values.get("getadvice")
        date = now.strftime("%Y-%m-%d")
        # 預先發給秘書部和會長分流，決定要最後要給誰
        sorter = db.session.execute('select id from manager where apartment = "秘書部"').fetchall()[0][0]
        leader = db.session.execute('select id from manager where apartment = "會長"').fetchall()[0][0]
        to_who_email = db.session.execute('select email from manager where apartment = "秘書部"').fetchall()[0][0]
        send_email("新案件審理提醒", "{}/".format(app_host), to_who_email)
        to_who_email = db.session.execute('select email from manager where apartment = "會長"').fetchall()[0][0]
        send_email("新案件審理提醒", "{}/".format(app_host), to_who_email)
        db.session.add(report(str(ind+1), anonymous, sender, sender_id, publish, form_type, content, to_who, str(sorter), advice, date, "", "", ""))
        db.session.add(report(str(ind+2), anonymous, sender, sender_id, publish, form_type, content, to_who, str(leader), advice, date, "", "", ""))
        db.session.commit()
        return render_template('index.html')
    return render_template('report.html')

# 信箱
@app.route('/mailbox/<letters>', methods=['POST', 'GET'])
def mailbox(letters):
    if session['manager_login'] or session['login']:
        # 條列郵件
        condition = session.get('id')
        mails = db.session.execute('select * from report where receiver = "{}"'.format(condition)).fetchall()
        retrun_mails = db.session.execute('select * from report where sender_id = "{}"'.format(condition)).fetchall()
        if request.method=="POST":
            # 若有回覆信件會進入這個判斷
            sender = request.values.get('sender')
            return_massage = request.values.get('return_massege')
            progress = request.values.get('progress')
            db.session.execute('update report set return_massege = "{}", progress = "{}" where ind = "{}"'.format(return_massage, progress, sender))
            db.session.commit()
            return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = 'all')
        if session['manager_login'] and (session['apartment'] == '秘書部' or session['apartment'] == "會長"):
            managers = db.session.execute('select id, name, apartment from manager').fetchall()
            return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = letters, managers = managers)
        return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = letters)
    else:
        return redirect(url_for('login', errors = ""))

# 分流時改變收件者
@app.route('/change_receiver/<receiver>/<letter_id>', methods=['POST', 'GET'])
def change_receiver(receiver, letter_id):
    if session['manager_login']:
        send_email("新案件審理提醒", "{}/".format(app_host), db.session.execute("select email from manager where id='{}'".format(receiver)).fetchall()[0][0])
        db.session.execute('update report set receiver = "{}" where ind = {}'.format(receiver, letter_id))
        db.session.commit()
    return redirect( url_for('mailbox', letters = 'all'))

# 新增最新消息
@app.route('/addinfo/<order>', methods=['POST', 'GET'])
def addinfo(order):
    temp = db.session.execute('select ind from info order by ind').fetchall()
    try:
        ind = max(temp[-1])
    except:
        ind = 0
    if order == "adjust":
        # 若是更改消息會進這個判斷，這邊沒寫好，得刪除再新增
        db.session.execute('delete from info where ind = {}'.format(ind))
    if session['manager_login']:
        if request.method == "POST":
            title = request.values.get("gettitle")
            try:
                content = '<br>'.join(request.values.get("getcontent").split('\r\n'))
            except:
                content = request.values.get("getcontent")
            try:
                document = '|'.join(request.values.get("getdocument").split('\r\n'))
            except:
                document = request.values.get("getdocument")
            apartment = request.values.get("getapartment")
            y = request.values.get("y")
            m = request.values.get("m")
            d = request.values.get("d")
            if document == '':
                document = '無'
            db.session.add(info(ind+1, title, content, document, apartment, y+"-"+m+"-"+d))
            db.session.commit()
            # print(ind+1, title, content, document, apartment, y+"-"+m+"-"+d)
        return render_template('addinfo.html')
    else:
        return redirect(url_for('login', errors = ""))

# @app.route('/addlaws/<step>', methods=['POST', 'GET'])
# def addlaws(step):
#     if request.method == "POST":
#         if step == "2":
#             title = request.values.get("gettitle")
#             lawtype = request.values.get("gettype")
#             history = request.values.get("gethistory")
#             content = request.values.getlist("getcontent")
#             allchapter_type = request.values.get("all_getchapter_type")
#             temp = db.session.execute('select ind from law_name order by ind').fetchall()
#             try:
#                 ind = max(temp[-1])
#             except:
#                 ind = 0
#             date = now.strftime("%Y-%m-%d")
#             chapters = {"編":0,"章":0,"節":0,"款":0}
#             chapter_type = ["編", "章", "節", "款"]
#             ch_chapter = "一二三四五六七八九十"
#             allchapters = []
#             exchapter = '編'
#             for i in allchapter_type.split(" "):
#                 chapter = request.values.get(i)
#                 if exchapter != chapter and chapter_type.index(chapter) < chapter_type.index(exchapter):
#                     chapters[exchapter] = 0
#                 exchapter = chapter
#                 chapters[chapter] += 1
#                 if chapters[chapter] <= 10:
#                     allchapters.append("第"+ch_chapter[chapters[chapter]-1]+chapter)
#                 else:
#                     allchapters.append("第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter)
#             return render_template('addlaws.html', step = "2", title = title, history = history, ind = ind+1, lawtype = lawtype, allchapters = allchapters, content = content, chapter_adjust = chapter_adjust, length = len(allchapters))
#         elif step == "3":
#             title = request.values.get("gettitle")
#             lawtype = request.values.get("getlawtype")
#             history = request.values.get("gethistory")
#             date = now.strftime("%Y-%m-%d")
#             law_ind = request.values.get("getind")
#             allchapters = request.values.getlist("getchapter")
#             belong_chapter = request.values.getlist("getbelong_chapter")
#             allcontent = request.values.getlist("getcontent")
#             list_chapters = request.values.getlist("getlist_chapters")
#             temp = db.session.execute('select ind from law_name order by ind').fetchall()
#             try:
#                 ind = max(temp[-1])
#             except:
#                 ind = 0
#             db.session.add(law_name(ind+1, lawtype, title, history, list_chapters, date, ""))
#             temp = db.session.execute('select ind from laws order by ind').fetchall()
#             try:
#                 ind = max(temp[-1])
#             except:
#                 ind = 0
#             for i in range(len(allchapters)):
#                 db.session.add(laws(ind+1, int(law_ind), belong_chapter[i], allchapters[i], "<br>".join(allcontent[i].split("\r\n"))))
#                 ind += 1
#             db.session.commit()
#             return render_template('addlaws.html', step = "1")
#     return render_template('addlaws.html', step = step)

# 新增法律
@app.route('/addlaws', methods=['POST', 'GET'])
def addlaws():
    if session['manager_login']:
        if request.method == "POST":
            # 從表單接收資料
            title = request.values.get("gettitle")
            lawtype = request.values.get("gettype")
            history = request.values.get("gethistory")
            date = now.strftime("%Y-%m-%d")
            temp = db.session.execute('select ind from law_name').fetchall()
            # 獲取最後新增法律的id，+1以作為新法律id，若沒新法律則設為0+1
            try:
                law_title_ind = max(temp[-1])+1
            except:
                law_title_ind = 0
            # 新增法律
            db.session.add(law_name(law_title_ind, lawtype, title, history, "", date, ""))
            # 獲取最後新增法律細項的id，+1以作為新法律細項id，若沒新法律細項則設為0+1
            temp = db.session.execute('select ind from newlaws order by ind').fetchall()
            try:
                ind = max(temp[-1])+1
            except:
                ind = 0
            # 獲取法律細項之章節、條目和內容
            content = request.values.getlist("content")
            order = request.values.getlist('content-order')
            order_count = 0
            # 此四容器為計算目前為第幾章節，並轉換成中文數字
            chapters = {"編":0,"章":0,"節":0,"款":0}
            chapter_type = ["編", "章", "節", "款"]
            ch_chapter = "一二三四五六七八九十"
            exchapter = '編'
            
            for i in content:
                # 偵測是否為章節(章節資料回格式為 數字_名稱 )，並新增至資料庫
                if i[1] == "_":
                    chapter, chapter_name = i.split("_")
                    if exchapter != chapter and chapter_type.index(chapter) < chapter_type.index(exchapter):
                        chapters[exchapter] = 0
                    exchapter = chapter
                    chapters[chapter] += 1
                    if chapters[chapter] <= 10:
                        chapter="第"+ch_chapter[chapters[chapter]-1]+chapter
                    else:
                        chapter="第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter
                    db.session.add(newlaws(ind+1, law_title_ind, chapter+" "+chapter_name, "", ""))
                # 偵測是否為條目內容，並新增至資料庫
                else:
                    db.session.add(newlaws(ind+1, law_title_ind, "", str(order[order_count]), i))
                    order_count += 1
                ind += 1
            db.session.commit()
            return render_template('newaddlaw.html')
        return render_template('newaddlaw.html')
    else:
        return redirect(url_for('login', errors = ""))

# 新增會議紀錄
@app.route('/addrecord', methods=['POST', 'GET'])
def addrecord():
    temp = db.session.execute('select ind from record order by ind').fetchall()
    try:
        ind = max(temp[-1])
    except:
        ind = 0
    if session['manager_login']:
        if request.method == "POST":
            title = request.values.get("gettitle")
            try:
                form = '|'.join(request.values.get("getform").split('\r\n'))
            except:
                form = request.values.get("getform")
            try:
                video = '|'.join(request.values.get("getvideo").split('\r\n'))
            except:
                video = request.values.get("getvideo")
            apartment = request.values.get("getapartment")
            y = request.values.get("y")
            m = request.values.get("m")
            d = request.values.get("d")
            if video == '':
                video = '無'
            if form == '':
                form = '無'
            db.session.add(record(ind+1, title, form, video, apartment, y+"-"+m+"-"+d))
            db.session.commit()
        return render_template('addrecord.html')
    else:
        return redirect(url_for('login', errors = ""))

# 申請政黨頁面前置
@app.route('/applyrule')
def applyrule():
    return render_template("applyrule.html")

# 申請政黨
@app.route('/applyparty', methods=['POST', 'GET'])
def applyparty():
    if session['manager_login'] or session['login']:
        if request.method == "POST":     
            dir = 'static/uploads/'
            # 因為要接收資料，我開一個佔存資料夾，這邊若有兩人以上同時使用可能會有bug，可能需要修一下
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            charger = request.files['charger']
            application = request.files['application']
            icon = request.files['icon']
            member = request.files['member']
            documents = [charger, application, icon, member]
            for d in documents:
                d.save(os.path.join("static/uploads/", d.filename))
            # 注意這邊用send_data，檔案要用這個寄
            send_data("政黨申請提醒", render_template('applypartymail.html'), "kssa.autonomy@gmail.com")
            return redirect(url_for('applyrule', charger = charger, application = application, icon = icon, member = member))
        return render_template("applyparty.html")

@app.route('/applyplace', methods=['POST', 'GET'])
def applyplace():
    if session['manager_login'] or session['login']:
        if request.method == 'POST':
            applier = request.values.get("applier")
            charger = request.values.get("charger")
            year = request.values.get("year")
            month = request.values.get("month")
            date = request.values.get("date")
            place = request.values.get("place")
            # to_who = db.session.execute('select email from manager where apartment = "自治部"').fetchone()[0]
            send_email("場地申請提醒", render_template("applyplacemail.html", applier=applier, charger=charger, year=year, month=month, date=date, place=place), "kssa.autonomy@gmail.com")
            return redirect(url_for('applyrule'))
        return render_template("applyplace.html")