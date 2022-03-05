from flask import Flask, render_template,redirect, session, url_for, request, jsonify
from flask import Flask
import os
import json

from sqlalchemy.sql.sqltypes import Integer
from flask_sqlalchemy import SQLAlchemy
import pymysql
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.dialects.mysql import LONGTEXT
pymysql.install_as_MySQLdb()

app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://ejbmw8g7yhmi4c0u:b3s9faj385y2lb2c@kutnpvrhom7lki7u.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/q9cbstir0fhhvua3"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column('id', db.String(100), primary_key=True)
    name = db.Column('name', db.String(100))
    password = db.Column('password', db.String(100))
    email = db.Column('email', db.String(100))
    enteryear = db.Column('enteryear', db.String(100))
    def __init__(self, id, name, password, email, enteryear):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.enteryear = enteryear

class manager(db.Model):
    __tablename__ = 'manager'
    id = db.Column('id', db.String(100), primary_key=True)
    name = db.Column('name', db.String(100))
    password = db.Column('password', db.String(100))
    email = db.Column('email', db.String(100))
    enteryear = db.Column('enteryear', db.String(100))
    apartment = db.Column('apartment', db.String(100))
    activate = db.Column('activate', Integer)
    def __init__(self, id, name, password, email, enteryear, apartment, activate):
        self.id = id
        self.name = name
        self.password = password
        self.email = email
        self.enteryear = enteryear
        self.apartment = apartment
        self.activate = activate

class info(db.Model):
    __tablename__ = 'info'
    ind = db.Column('ind', Integer, primary_key=True)
    title = db.Column('title', db.String(100))
    content = db.Column('content', db.Text(10000000))
    document = db.Column('document', db.String(100))
    apartment = db.Column('apartment', db.String(100))
    date = db.Column('date', db.String(100))
    def __init__(self, ind, title, content, document, apartment, date):
        self.ind = ind
        self.title = title
        self.content = content
        self.document = document
        self.apartment = apartment
        self.date = date

# class vote(db.Model):
#     __tablename__ = 'vote'
#     ind = db.Column('ind', Integer, primary_key=True)
#     topic = db.Column('topic', db.String(100))
#     holder = db.Column('holder', db.String(100))
#     options = db.Column('options', db.Text(10000000))
#     result = db.Column('result', db.String(1000))
#     result_t = db.Column('result_t', db.String(1000))
#     activate = db.Column('activate', Integer)
#     participate = db.Column('participate', db.String(1000))
#     address = db.Column('address', db.String(100))
#     def __init__(self, ind, topic, holder, options, result, result_t, activate, participate, address):
#         self.ind = ind
#         self.topic = topic
#         self.holder = holder
#         self.options = options
#         self.result = result
#         self.result_t = result_t
#         self.activate = activate
#         self.participate = participate
#         self.address = address

class record(db.Model):
    __tablename__ = 'record'
    ind = db.Column('ind', Integer, primary_key=True)
    apartment = db.Column('apartment', db.String(100))
    title = db.Column('title', db.String(100))
    form = db.Column('form', db.Text(10000000))
    video = db.Column('video', db.Text(1000000))
    date = db.Column('date', db.String(100))
    def __init__(self, ind, title, form, video, apartment, date):
        self.ind = ind
        self.title = title
        self.form = form
        self.video = video
        self.apartment = apartment
        self.date = date

class laws(db.Model):
    __tablename__ = 'laws'
    ind = db.Column('ind', Integer, primary_key=True)
    law_ind = db.Column('law_type_ind', Integer)
    belong_chapter = db.Column('belong_chapter', db.String(1000))
    chapter = db.Column('chapter', db.String(1000))
    content = db.Column('content', db.Text(10000000))
    def __init__(self, ind, law_ind, chapter, belong_chapter, content):
        self.ind = ind
        self.law_ind = law_ind
        self.chapter = chapter
        self.belong_chapter = belong_chapter
        self.content = content

class law_name(db.Model):
    __tablename__ = 'law_name'
    ind = db.Column('ind', Integer, primary_key=True)
    law_type = db.Column('law_type', db.String(100))
    title = db.Column('title', db.String(100))
    history = db.Column('history', db.Text(10000000))
    date = db.Column('date', db.String(100))
    mod_date = db.Column('mod_date', db.String(100))
    def __init__(self, ind, law_type, title, history, date, mod_date):
        self.ind = ind
        self.law_type = law_type
        self.title = title
        self.history = history
        self.date = date
        self.mod_date = mod_date

class report(db.Model):
    __tablename__ = 'report'
    ind = db.Column('ind', Integer, primary_key=True)
    anonymous = db.Column('anonymous', db.String(15))
    sender_id = db.Column('sender_id', db.String(100))
    sender_name = db.Column('sender_name', db.String(100))
    publish = db.Column('publish', db.String(100))
    form_type = db.Column('form_type', db.String(100))
    content = db.Column('content', db.Text(10000000))
    to_who = db.Column('to_who', db.Text(100))
    receiver = db.Column('receiver', db.Text(100))
    advice = db.Column('advice', db.Text(10000000))
    sned_date = db.Column('sned_date', db.String(100))
    return_date = db.Column('return_date', db.String(100))
    progress = db.Column('progress', db.String(15))
    return_massege = db.Column('return_massege', db.Text(10000000))
    def __init__(self, ind, anonymous, sender_name, sender_id, publish, form_type, content, to_who, receiver, advice ,sned_date,return_date, progress, return_massege):
        self.ind = ind
        self.anonymous = anonymous
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.publish = publish
        self.form_type = form_type
        self.content = content
        self.to_who = to_who
        self.receiver = receiver
        self.advice = advice
        self.sned_date = sned_date
        self.return_date = return_date
        self.progress = progress
        self.return_massege =return_massege

class allleaders(db.Model):
    period = db.Column('period', db.String(15), primary_key=True)
    leader = db.Column('leader', db.String(15))
    secondleader = db.Column('secondleader', db.String(15))
    year = db.Column('year', Integer)
    def __init__(self, period, leader, secondleader, year):
        self.period = period
        self.leader = leader
        self.secondleader = secondleader
        self.year = year

class allspeaker(db.Model):
    period = db.Column('period', db.String(15), primary_key=True)
    speaker = db.Column('speaker', db.String(15))
    secondspeaker = db.Column('secondspeaker', db.String(15))
    year = db.Column('year', Integer)
    def __init__(self, period, speaker, secondspeaker, year):
        self.period = period
        self.speaker = speaker
        self.secondspeaker = secondspeaker
        self.year = year

@app.route('/')
def index():
    db.drop_all()
    # Create data
    test = manager("099999", 'manager1', "test",'vincent.super8@gmail.com', '2020', '學生議會秘書處', 1)
    test5 = manager("099998", 'manager2', "test",'vincent.super8@gmail.com', '2021', '自治部', 1)
    test2 = manager("099997", 'sorter', "sorter",'vincent.super8@gmail.com', '2021', '分類者', 1)
    test6 = manager("100000", 'speaker', "speaker",'vincent.super8@gmail.com', '2021', '議長', 1)
    test7 = manager("100001", 'chairman', "chairman",'vincent.super8@gmail.com', '2021', '會長', 1)
    test3 = User("090000", 'test1', "test",'vincent.super8@gmail.com', '2020')
    test4 = User("090001", 'test2', "test",'vincent.super8@gmail.com', '2021')
    db.create_all()
    db.session.add(test)
    db.session.add(test2)
    db.session.add(test3)
    db.session.add(test4)
    db.session.add(test5)
    db.session.add(test6)
    db.session.add(test7)
    db.session.commit()
    return 'ok'


if __name__ == "__main__":
    app.run(debug=True)