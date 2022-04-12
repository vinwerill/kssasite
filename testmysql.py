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
from createdb import laws
from createdb import allspeaker

# from flask_migrate import Migrate

app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://hfcv0x0q041lmavo:vsacpso5298i52g9@m7az7525jg6ygibs.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/xkbq7dgi25ki89nk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

db.session.add(law_name(8, "自治條例", "高雄市立高雄高級中學學生聯合自治會預算決算自治條例", "中華民國 103 年 06 月 13 日經班代大會決議通過制定公布預算法 34 條、決算法 23 條<br><br>中華民國 104 年 05 月 12 日經學生代表大會決議通過修正預算法 34 條、決算法 23 條<br><br>中華民國 106 年 01 月 16 日雄中學聯行字第 1050005 號令，修正本自治條例名稱，並修正全文 54 條", "總則-預算-預算之編擬與提出-預算之審議-預算之執行-特別預算與追加預算-決算-決算之編造-決算之審核-附則", "2022-04-11", ""))
db.session.commit()