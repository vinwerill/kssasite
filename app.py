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
from createdb import manager, info, report, User, record, laws, law_name, allleaders, allspeaker, vote, parliamentary, conference
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

def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
        'favicon.ico', mimetype='image/x-icon')

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

@app.route('/show_manager')
def show_manager():
    if session['manager_login'] and (session['apartment'] == "議長" or session['apartment'] =="會長"):
        managers = db.session.execute('select * from manager').fetchall()
        return render_template('show_manager.html', managers = managers)

@app.route('/change_speaker/<step>', methods = ['POST', 'GET'])
def change_speaker(step):
    if session['manager_login'] and (session['apartment'] == "議長" or session['apartment'] =="會長"):
        if request.method == "POST":
            if step == "2":
                target = request.values.get(request.values.get("target"))
                return render_template('change_speaker.html', target = target, step = step)
            elif step == "3":
                target = request.values.get("target")
                db.session.execute('update manager set apartment = "議長" where id = "{}"'.format(target))
                db.session.execute('update manager set apartment = "" where id = "{}"'.format(session["id"]))
                db.session.commit()
                session["apartment"] = ""
                return redirect(url_for('adjust_ident', step = 1))
        managers = db.session.execute('select * from manager').fetchall()
        return render_template('change_speaker.html', managers = managers, step = step)

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

@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == "POST":
        email = request.values.get("email")
        usertype = request.values.get("type")
        if User.query.filter_by(email = email).first() != None and usertype == "User":
            send_email("密碼遺失備援", render_template('password.html', password = User.query.filter_by(email = email).first().password), email)
        elif User.query.filter_by(email = email).first() != None and usertype == "manager":
            send_email("密碼遺失備援", render_template('password.html', password = manager.query.filter_by(email = email).first().password), email)
        return render_template('forget_password.html', send = 1)
    return render_template('forget_password.html', send = 0)

@app.route('/login', methods=['POST', 'GET'])
def login():
    session['user'] = ""
    session['login'] = False
    session['manager_login'] = False
    return render_template('login.html', errors = "", active = "User_login")

@app.route('/about_adminstraion')
def about_adminstraion():
    return render_template('about_adminstration.html')

@app.route('/manager_login', methods=['POST', 'GET'])
def manager_login():
    if request.method=="POST":
        ident = request.values.get("id")
        password = request.values.get("password")
        found_user = manager.query.filter_by(id = ident).first()
        if found_user != None:
            check_password = manager.query.filter_by(id = ident).first().password
            if check_password == password:
                session['user'] = manager.query.filter_by(id = ident).first().name
                session['apartment'] = manager.query.filter_by(id = ident).first().apartment
                session['manager_login'] = True
                session['id'] = ident
                return render_template('index.html')
            else:
                session['manager_login'] = False
                return render_template('login.html', errors = "管理員密碼錯誤", active = "manager_login")
        else:
            return render_template('login.html', errors = "該管理員學號未註冊，請註冊或重新輸入", active = "manager_login")
    return render_template('login.html', errors = "", active = "manager_login")

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
        if manager.query.filter_by(id = ident).first():
            if order == 'adjust' and session["id"] == ident:
                pass
            else:
                return render_template('manager_register.html', errors = "該學號已經存在，請重新輸入")
        if len(ident) != 6:
            return render_template('manager_register.html', errors = "學號長度為六碼，請重新輸入")
        if checkpassword != password:
            return render_template('manager_register.html', errors = "密碼與確認密碼不同，請確認並重新輸入")
        if ident == "" or user == "" or password == "" or email == "" or enteryear == "" or apartment == "":
            return render_template('manager_register.html', errors = "所有表格皆須填入，請重新輸入")
        if order == 'adjust':
            db.session.execute("DELETE FROM manager where id = '{}'".format(ident))
        try:
            db.session.add(manager(ident, user, password, email, enteryear, apartment, exist[order]))
            db.session.commit()
        except OperationalError:
            os.system("heroku restart -a kssasite")
            db.session.add(manager(ident, user, password, email, enteryear, apartment, exist[order]))
            db.session.commit()
            return render_template('waitcommit.html', user=user, login = True)
        if order == 'register':
            send_email("管理員申請核可確認", render_template('activation.html', actlink = '{}/actlink/{}'.format(app_host, ident)), 'jonny30904@gmail.com')
            return render_template('wait_for_activating.html')
        else:
            return redirect(url_for('index'))
    return render_template('manager_register.html', errors = "")

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
        except OperationalError:
            os.system("heroku restart -a kssasite")
            db.session.add(User(ident, user, password, email, enteryear))
            db.session.commit()
            return render_template('waitcommit.html', user=user, login = True)
    return render_template('register.html', errors = "")

@app.route('/adjust_ident', methods=['POST', 'GET'])
def adjust_ident():
    if session['manager_login']:
        ident = list(db.session.execute("select * from manager where id = '{}'".format(session["id"])))[0]
        return render_template('adjust_managerident.html', ident = ident)
    elif session['login']:
        ident = list(db.session.execute("select * from User where id = '{}'".format(session["id"])))[0]
        return render_template('adjust_userident.html', ident = ident)

@app.route('/actlink/<account>', methods=['POST', 'GET'])
def actlink(account):
    if request.method == "POST":
        password = request.values.get("password")
        db.session.execute('update manager set activate = 1 where id = "{}"'.format(1, account))
        db.session.commit()
        return render_template('actlink.html', confirm = 0, wac = account, condition = 2)
        # else:
        #     return render_template('actlink.html', confirm = 0, wac = account, condition = 1)
    return render_template('actlink.html', confirm = 0, wac = account, condition = 0)

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

@app.route('/addleader', methods=['POST', 'GET'])
def addleader():
    if request.method == 'POST':
        period = request.values.get('getperiod')
        leader = request.values.get('getleader')
        secondleader = request.values.get('getsecondleader')
        year = request.values.get('getyear')
        try:
            db.session.add(allleaders(period, leader, secondleader, year))
        except:
            db.session.execute('update allleaders set leader = "{}", secondleader = "{}" where period = "{}"'.format(leader, secondleader, period))
        db.session.commit()
        return render_template('addleader.html')
    return render_template('addleader.html')

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

@app.route('/showspeaker', methods=['POST', 'GET'])
def showspeaker():
    contents = db.session.execute("select * from allspeaker order by year desc")
    return render_template('showspeaker.html', contents = contents)

@app.route('/showleader', methods=['POST', 'GET'])
def showleader():
    contents = db.session.execute("select * from allleaders order by year desc")
    return render_template('showleader.html', contents = contents)


@app.route('/set_conference', methods=['POST', 'GET'])
def set_conference():
    if session['manager_login']:
        # temp = db.session.execute('select ind from vote order by ind').fetchall()
        # try:
        #     ind = temp[-1][0]
        # except:
        #     ind = 0
        # db.session.add(vote(ind+1, session['id'], "", "", 1))
        check_exist = db.session.execute("select * from conference").fetchall()[0]
        # print(check_exist)
        if check_exist[0] == 0:
            try:
                db.session.execute("update parliamentary set choice = '', participation = 0")
                db.session.execute("update conference set activation = 1, result = ''")
                db.session.commit()
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

@app.route('/vote/<m>', methods=['POST', 'GET'])
def vote_page(m):
    if session['manager_login']:
        check_exist = db.session.execute("select * from conference").fetchall()[0]
        if m == "end":
            if request.method == "POST":
                choice = request.values.get('choice')
                # ind = request.values.get('ind')
                # choice = request.values.get('choice')
                # old_participant = db.session.execute('select participant from vote where ind = {}'.format(ind)).fetchall()[0][0]
                # if session['user'] in old_participant:
                #     return render_template("vote.html", m = "result", ind = ind)
                # update_participant = old_participant+"-"+session['user']
                # old_choice = db.session.execute('select choice from vote where ind = {}'.format(ind)).fetchall()[0][0]
                # update_choice = old_choice+"-"+choice
                db.session.execute('update parliamentary set choice = "{}" where name = "{}"'.format(choice, session['user']))
                db.session.commit()

            return render_template("vote.html", m = "vote", exist = 1)
        elif m == "vote":
            if check_exist[0] == 1:
                try:
                    db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
                    db.session.commit()
                except OperationalError:
                    os.system("heroku restart -a kssasite")
                    db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
                    db.session.commit()
                return render_template("vote.html", m = "vote", exist = 1)
            else:
                return render_template("vote.html", m = "vote", exist = 0)
        elif m == "checkout":
            if request.method == "POST":
                db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
                db.session.commit()
                return redirect(url_for('vote_page', m='vote'))
            # try:
            #     return render_template("vote.html", m = "checkout", exist = 1)
            # except OperationalError:
            #     os.system("heroku restart -a kssasite")
            return render_template("vote.html", m = "checkout", exist = 1)

        elif m == "rejoin":
            return render_template("vote.html", m = "checkout", exist = 1)

        elif m == "result":
            if check_exist[0] == 1:
                return render_template("vote.html", m = "result", exist = 1)
            else:
                return render_template("vote.html", m = "result", exist = 0)

        elif m == "conclusion":
            result = list(map(int, request.values.get('conclusion').split("-")))
            db.session.execute("update parliamentary set choice = 'adstain' where choice = 'none'")
            db.session.execute("update conference set activation = 0")
            db.session.commit()
            return render_template("vote.html", m = "conclusion", result = result)
        
    else:
        return redirect(url_for('User_login'))


# @app.route('/show_vote/<ind>', methods=['POST', 'GET'])
# def show_vote(ind):
#     options = db.session.execute('select options from vote where ind = {}'.format(ind)).fetchall()[0][0].split("-")
#     topic = db.session.execute('select topic from vote where ind = {}'.format(ind)).fetchall()[0][0]
#     return render_template('vote.html', m = "result", ind = ind, options = options, length = len(options), topic = topic)

# @app.route('/getoptions/<topic>', methods=['POST', 'GET'])
# def getoptions(topic):
#     participant = db.session.execute('select participant from vote where ind = {}'.format(topic)).fetchall()[0][0].split("-")
#     choice = db.session.execute('select choice from vote where ind = {}'.format(topic)).fetchall()[0][0].split("-")
#     return {"participant":participant, 'choice':choice}

@app.route('/getparliamentary', methods=['POST', 'GET'])
def getparliamentary():
    try:
        db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
        db.session.commit()
    except OperationalError:
        os.system("heroku restart -a kssasite")
        db.session.execute('update parliamentary set participation = 1, choice = "none" where name = "{}"'.format(session['user']))
        db.session.commit()
    temp = db.session.execute('select * from parliamentary order by ind').fetchall()
    data = []
    for i in temp:
        tempdict = {}
        tempdict['name'] = i[1]
        tempdict['choice'] = i[2]
        tempdict['participation'] = i[3]
        data.append(tempdict)
    data = json.dumps(data)
    # print(data)
    return {'data':data}

@app.route('/getconferenceact', methods=['POST', 'GET'])
def getconferenceact():
    try:
        temp = db.session.execute('select * from conference').fetchall()[0][0]
    except OperationalError:
        os.system("heroku restart -a kssasite")
        temp = db.session.execute('select * from conference').fetchall()[0][0]
    return {'data':temp}



@app.route('/laws/<order>')
def laws_web(order):
    if order == 'all':
        constitution = db.session.execute('select * from law_name where law_type like "%組織章程%"').fetchall()
        ordinance = db.session.execute('select * from law_name where law_type like "%自治條例%" order by ind').fetchall()
        rule = db.session.execute('select * from law_name where law_type like "%自治規則%"').fetchall()
        return render_template('laws.html', order = order, constitution = constitution, ordinance = ordinance, rule = rule)
    else:
        title = db.session.execute('select * from law_name where ind = {}'.format(order)).fetchall()[0]
        temp = db.session.execute('select chapter from laws where law_type_ind = {}'.format(order)).fetchall()
        allchapters = []
        for i in temp:
            if i in allchapters:
                pass
            else:
                allchapters.append(i)
        return render_template('laws.html', order = order, title = title, allchapters = allchapters)

@app.route('/show_laws')
def show_laws():
    if session['manager_login']:
        laws_title = db.session.execute('select * from law_name').fetchall()
        return render_template('show_laws.html', laws_title = laws_title)

@app.route('/adjust_laws/<ind>/<step>', methods=['POST', 'GET'])
def adjust_laws(ind, step):
    if request.method == "POST":
        if step == "2":
            title = request.values.get("gettitle")
            lawtype = request.values.get("gettype")
            history = request.values.get("gethistory")
            content = request.values.getlist("getcontent")
            allchapter_type = request.values.get("all_getchapter_type")
            temp = db.session.execute('select ind from law_name order by ind').fetchall()
            try:
                ind = max(temp[-1])
            except:
                ind = 0
            date = now.strftime("%Y-%m-%d")
            chapters = {"編":0,"章":0,"節":0,"款":0}
            chapter_adjust_list = {
               "編":{"編":"0%","章":"10%","節":"20%","款":"30%"}, "章":{"章":"0%","節":"10%","款":"20%"},"節":{"節":"0%","款":"10%"}
            }
            chapter_adjust = chapter_adjust_list[request.values.get(allchapter_type.split(" ")[0])]
            exchapter = '章'
            ch_chapter = "一二三四五六七八九十"
            allchapters = []
            originallaws = db.session.execute("select * from laws where law_type_ind = {}".format(ind)).fetchall()
            for i in allchapter_type.split(" "):
                chapter = request.values.get(i)
                if chapter == None:
                    continue
                chapters[chapter] += 1
                if chapters[chapter] <= 10:
                    allchapters.append("第"+ch_chapter[chapters[chapter]-1]+chapter)
                else:
                    allchapters.append("第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter)
            return render_template('adjustlaws.html', step = "2", title = title, history = history, ind = ind, lawtype = lawtype, allchapters = allchapters, chapter_adjust = chapter_adjust,content = content, length = len(allchapters), originallaws = originallaws)
    law_title = db.session.execute('select * from law_name where ind = {}'.format(ind)).fetchall()[0]
    temp = db.session.execute('select chapter from laws where law_type_ind = {}'.format(ind)).fetchall()
    allchapters = []
    for i in temp:
        if list(i[0].split(' ')) in allchapters:
            pass
        else:
            allchapters.append(list(i[0].split(' ')))
    return render_template('adjustlaws.html', ind = ind, step = step, law_title =law_title, allchapters = allchapters, length = len(allchapters))

@app.route('/getlaws/<law>', methods=['POST', 'GET'])
def getlaws(law):
    content = db.session.execute('select * from laws where law_type_ind = "{}" order by ind'.format(law)).fetchall()
    for i in range(len(content)):
        content[i] = list(content[i])
    return {'all_laws':content}

@app.route('/gethistory/<history>', methods=['POST', 'GET'])
def gethistory(history):
    result = db.session.execute('select * from law_name where ind = "{}" order by ind'.format(history)).fetchall()
    for i in range(len(result)):
        result[i] = list(result[i])
    return {'history':result}

@app.route('/info/<order>')
def info_web(order):
    content = []
    if order == 'all':
        # adminstration = db.session.execute('select * from info where apartment like "%學聯會-%"').fetchall()
        # parliament = db.session.execute('select * from info where apartment like "%學生議會-%"').fetchall()
        # boardofinquiry = db.session.execute('select * from info where apartment like "%評議委員會-%"').fetchall()
        all_infos = db.session.execute('select * from info').fetchall()
        return render_template('info.html', infos=all_infos, content = content, order = order)
    else:
        content = db.session.execute('select * from info where ind = {}'.format(order)).fetchall()
        # print(content)
        return render_template('info.html', order = order, content = content[0])

@app.route('/show_info')
def show_info():
    if session['manager_login']:
        infos = db.session.execute('select * from info').fetchall()
        # print(infos)
        return render_template('show_info.html', infos = infos)

@app.route('/adjust_info/<ind>', methods = ['POST', 'GET'])
def adjust_info(ind):
    if session['manager_login']:
        info = db.session.execute('select * from info where ind = {}'.format(ind)).fetchall()
        return render_template('adjust_info.html', info = info[0])

@app.route('/record/<order>')
def record_web(order):
    content = []
    if order == 'all':
        adminstration = db.session.execute('select * from record where apartment like "%學聯會-%"').fetchall()
        parliament = db.session.execute('select * from record where apartment like "%學生議會-%"').fetchall()
        return render_template('record.html', adminstration = adminstration, parliament = parliament, order = order, content = content)
    else:
        content = db.session.execute('select * from record where ind = {}'.format(order)).fetchall()[0]
        return render_template('record.html', order = order, content = content)

@app.route('/show_record')
def show_record():
    if session['manager_login']:
        records = db.session.execute('select * from record').fetchall()
        # print(records[0])
        return render_template('show_record.html', records = records)

@app.route('/adjust_record/<ind>')
def adjust_record(ind):
    if session['manager_login']:
        record = db.session.execute('select * from record where ind = {}'.format(ind)).fetchall()
        return render_template('adjust_record.html', record = record[0])

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
        db.session.execute('delete from laws where law_type_ind = {}'.format(target))
    if t == "manager":
        db.session.execute('delete from manager where id = {}'.format(target))
    else:
         db.session.execute('delete from {} where ind = {}'.format(t, target))
    db.session.commit()
    return render_template('index.html', target_id = target)

@app.route('/report', methods=['POST', 'GET'])
def report_web():
    if request.method=="POST":
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
        publish = request.values.get("agreement")
        form_type = ' '.join(request.values.getlist("type"))
        try:
            content = '<br>'.join(request.values.get("getcontent").split('\r\n'))
        except:
            content = request.values.get("getcontent")
        to_who = '<br>'.join(request.values.getlist("towho"))
        try:
            advice = '<br>'.join(request.values.get("getadvice").split('\r\n'))
        except:
            advice = request.values.get("getadvice")
        date = now.strftime("%Y-%m-%d")
        sorter = db.session.execute('select id from manager where apartment = "秘書部"').fetchall()[0][0]
        leader = db.session.execute('select id from manager where apartment = "會長"').fetchall()[0][0]
        # print('-'*20)
        # print(ind)
        # print('-'*20)
        to_who_email = db.session.execute('select email from manager where apartment = "秘書部"').fetchall()[0][0]
        send_email("新案件審理提醒", "{}/".format(app_host), to_who_email)
        to_who_email = db.session.execute('select email from manager where apartment = "會長"').fetchall()[0][0]
        send_email("新案件審理提醒", "{}/".format(app_host), to_who_email)
        db.session.add(report(str(ind+1), anonymous, sender, sender_id, publish, form_type, content, to_who, str(sorter), advice, date, "", "", ""))
        db.session.add(report(str(ind+2), anonymous, sender, sender_id, publish, form_type, content, to_who, str(leader), advice, date, "", "", ""))
        db.session.commit()
        return render_template('index.html')
    return render_template('report.html')

@app.route('/mailbox/<letters>', methods=['POST', 'GET'])
def mailbox(letters):
    if session['manager_login'] or session['login']:
        condition = session.get('id')
        mails = db.session.execute('select * from report where receiver = "{}"'.format(condition)).fetchall()
        retrun_mails = db.session.execute('select * from report where sender_id = "{}"'.format(condition)).fetchall()
        if request.method=="POST":
            sender = request.values.get('sender')
            return_massage = request.values.get('return_massege')
            progress = request.values.get('progress')
            db.session.execute('update report set return_massege = "{}", progress = "{}" where ind = "{}"'.format(return_massage, progress, sender))
            db.session.commit()
            # ind = db.session.execute('select sender_id form report whereind = "{}'.format(sender)).fetchall()[0][0]
            # email = db.session.execute('select email from users where id = "{}"'.format(ind)).fetchall()[0][0]
            # if email == '':
            #     email = db.session.execute('select email from manager where id = "{}"'.format(ind)).fetchall()[0][0]
            # send_email("新案件審理提醒", "{}/".format(app_host), email)
            return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = 'all')
        if session['manager_login'] and (session['apartment'] == '秘書部' or session['apartment'] == "會長"):
            managers = db.session.execute('select id, name, apartment from manager').fetchall()
            return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = letters, managers = managers)
        return render_template('mailbox.html', mails = mails, retrun_mails = retrun_mails, letters = letters)
    else:
        return redirect(url_for('login', errors = ""))

@app.route('/change_receiver/<receiver>/<letter_id>', methods=['POST', 'GET'])
def change_receiver(receiver, letter_id):
    if session['manager_login']:
        send_email("新案件審理提醒", "{}/".format(app_host), db.session.execute("select email from manager where id='{}'".format(receiver)).fetchall()[0][0])
        db.session.execute('update report set receiver = "{}" where ind = {}'.format(receiver, letter_id))
        db.session.commit()
    return redirect( url_for('mailbox', letters = 'all'))

@app.route('/addinfo/<order>', methods=['POST', 'GET'])
def addinfo(order):
    temp = db.session.execute('select ind from info order by ind').fetchall()
    try:
        ind = max(temp[-1])
    except:
        ind = 0
    if order == "adjust":
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

@app.route('/addlaws/<step>', methods=['POST', 'GET'])
def addlaws(step):
    if request.method == "POST":
        if step == "2":
            title = request.values.get("gettitle")
            lawtype = request.values.get("gettype")
            history = request.values.get("gethistory")
            content = request.values.getlist("getcontent")
            allchapter_type = request.values.get("all_getchapter_type")
            temp = db.session.execute('select ind from law_name order by ind').fetchall()
            try:
                ind = max(temp[-1])
            except:
                ind = 0
            date = now.strftime("%Y-%m-%d")
            chapters = {"編":0,"章":0,"節":0,"款":0}
            chapter_type = ["編", "章", "節", "款"]
            ch_chapter = "一二三四五六七八九十"
            allchapters = []
            chapter_adjust_list = {
               "編":{"編":"0%","章":"10%","節":"20%","款":"30%"}, "章":{"章":"0%","節":"10%","款":"20%"},"節":{"節":"0%","款":"10%"}
            }
            chapter_adjust = chapter_adjust_list[request.values.get(allchapter_type.split(" ")[0])]
            exchapter = '編'
            for i in allchapter_type.split(" "):
                chapter = request.values.get(i)
                if exchapter != chapter and chapter_type.index(chapter) < chapter_type.index(exchapter):
                    chapters[exchapter] = 0
                exchapter = chapter
                chapters[chapter] += 1
                if chapters[chapter] <= 10:
                    allchapters.append("第"+ch_chapter[chapters[chapter]-1]+chapter)
                else:
                    allchapters.append("第"+ch_chapter[chapters[chapter]//10-1]+"十"+ch_chapter[chapters[chapter]%10-1]+chapter)
            return render_template('addlaws.html', step = "2", title = title, history = history, ind = ind+1, lawtype = lawtype, allchapters = allchapters, content = content, chapter_adjust = chapter_adjust, length = len(allchapters))
        elif step == "3":
            title = request.values.get("gettitle")
            lawtype = request.values.get("getlawtype")
            history = request.values.get("gethistory")
            date = now.strftime("%Y-%m-%d")
            law_ind = request.values.get("getind")
            allchapters = request.values.getlist("getchapter")
            belong_chapter = request.values.getlist("getbelong_chapter")
            allcontent = request.values.getlist("getcontent")
            list_chapters = request.values.getlist("getlist_chapters")
            temp = db.session.execute('select ind from law_name order by ind').fetchall()
            try:
                ind = max(temp[-1])
            except:
                ind = 0
            db.session.add(law_name(ind+1, lawtype, title, "<br>".join(history.split("\r\n")), list_chapters, date, ""))
            temp = db.session.execute('select ind from laws order by ind').fetchall()
            try:
                ind = max(temp[-1])
            except:
                ind = 0
            for i in range(len(allchapters)):
                db.session.add(laws(ind+1, int(law_ind), belong_chapter[i], allchapters[i], "<br>".join(allcontent[i].split("\r\n"))))
                ind += 1
            db.session.commit()
            return render_template('addlaws.html', step = "1")
    return render_template('addlaws.html', step = step)

@app.route('/newaddlaw', methods=['POST', 'GET'])
def newaddlaw():
    if request.method == "POST":
        content = request.values.getlist("content")
        order = request.values.getlist('content-order')
        # print(content)
        # print(order)
        return render_template('newaddlaw.html')
    return render_template('newaddlaw.html')

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

@app.route('/applyrule')
def applyrule():
    return render_template("applyrule.html")

@app.route('/applyparty', methods=['POST', 'GET'])
def applyparty():
    if session['manager_login'] or session['login']:
        if request.method == "POST":     
            dir = 'static/uploads/'
            for f in os.listdir(dir):
                os.remove(os.path.join(dir, f))
            # basepath = os.path.join(os.path.dirname(__file__), 'static','uploads')
            charger = request.files['charger']
            application = request.files['application']
            icon = request.files['icon']
            member = request.files['member']
            documents = [charger, application, icon, member]
            for d in documents:
                d.save(os.path.join("static/uploads/", d.filename))
            # to_who = db.session.execute('select email from manager where apartment = "自治部"').fetchone()[0]
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