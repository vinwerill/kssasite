from flask import Flask, render_template,redirect, session, url_for, request, jsonify
from flask import Flask
import os
import json
from flask_sqlalchemy import SQLAlchemy
import pymysql
pymysql.install_as_MySQLdb()
from createdb import User
from createdb import info
from createdb import report
from createdb import manager
from createdb import law_name
from createdb import allleaders
from createdb import allspeaker

# from flask_migrate import Migrate

app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://root:1014vincentss@localhost:3306/kshsparliament"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

dict1 =db.session.execute('select * from laws').fetchall()
for i in dict1:
    print(i)