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
from createdb import allspeaker
from createdb import laws
from createdb import parliamentary
from createdb import conference
from createdb import allleaders
from createdb import allspeaker

# from flask_migrate import Migrate

app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://kssasite:kssaadmin@184.168.117.210:3306/kssadb"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://hfcv0x0q041lmavo:vsacpso5298i52g9@m7az7525jg6ygibs.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/xkbq7dgi25ki89nk"
# app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://gmmjduea_vincent:1014vincent@kssasite.com/gmmjduea_kssasite"
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://gmmjduea_site:gs1vT3FKU65Y@kssasite.com:3306/gmmjduea_kssasite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# db.session.execute('delete from newlaws where law_title_ind = 11')

# i = 1
# while True:
#     try:
#         element = input().split(", ")
#         db.session.add(parliamentary(i, *element))
#         i+=1
#     except EOFError:
#         break

# db.session.commit()
# db.session.execute('update conference set activation = 0')
# db.session.commit()
# if input("reset? y/n: ") == "y":
# db.session.execute("delete from laws")
# db.session.execute("delete from newlaws")
# db.session.execute("delete from law_name")
# db.session.commit()
temp = db.session.execute('select * from info').fetchall()
for i in temp:
    print(i)
# temp = db.session.execute('select * from newlaws').fetchall()
# for i in temp:
#     print(i)
# temp1 = db.session.execute('select law_title_ind from newlaws order by ind').fetchall()
# print(temp1)
# try:
#     law_title_ind = temp1[-1][0]+1
# except:
#     law_title_ind = 0
# print(law_title_ind)
# db.session.add(law_name(law_title_ind, "lawtype", "title", "history", "", "date", ""))
# db.session.commit()
# result = db.session.execute('select * from law_name').fetchall()
# print(result)
