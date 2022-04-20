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
from createdb import allspeaker

# from flask_migrate import Migrate

app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
# SHA-256 from 'flask20210112'
app.config['SECRET_KEY'] = '18f4173d24f63dd99d2700aad88002c61c864f83255f5c76da4a0002db1f31c4'
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://hfcv0x0q041lmavo:vsacpso5298i52g9@m7az7525jg6ygibs.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/xkbq7dgi25ki89nk"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# db.session.execute("update law_name set title = '高雄市立高雄高級中學學生聯合自治會行政中心組織自治條例' where ind = 2").fetchall()
# db.session.commit()
# temp = db.session.execute("select * from laws").fetchall()
# for i in temp:
#     print(i)
db.session.execute('delete from laws where ind = 454')
db.session.add(laws(454, 10, '第二節 政黨之財務', '26', '主管機關對於每屆全校不分區學生議員選舉得票率達百分之五以上之政黨，應編列年度預算補助之。 <br><br>前項補助，應由主管機關依當屆全校不分區學生議員選舉得票率依比例核算補助金額，通知政黨於十四天內掣據向主管機關領取。政黨未於規定期限內領取補助者，主管機關應催告其於一個月內具領；屆時未領取者，視為放棄。 <br><br>政黨依前項規定領取之補助，應用於競選費用、人事費用、政策研究費用及人才培育費用。'))
db.session.commit()
# (448, 10, '20', '第一節 政黨之組織及活動', '本會會員有加入或退出政黨之自由。 <br><br>')
# (449, 10, '21', '第一節 政黨之組織及活動', '非基於會員之自由意願，不得強制其加入或退出政黨。但對黨員為除名之處分者，不在此限。黨員身分之認定，以登載於黨員名冊者為準。 <br><br>)
# (450, 10, '22', '第一節 政黨之組織及活動', '政黨之章程，應載明下列事項： <br><br>一、名稱。有簡稱者，其簡稱。 <br><br>二、有標章者，其標章。 <br><br>三、宗旨。 <br><br>四、黨員之入黨、退黨、除名規則。 <br><br>五、黨員之權利及義務。 <br><br>六、負責人與選任人員之職稱、名額、產生方式、任期及解任。<br><br>七、黨員大會或黨員代表大會召集之條件、期限及決議方式。 <br><br>八、章程變更之程序。 <br><br>九、黨費之收取方式及數額。 <br><br>十、其他依法律規定應載明之事項。 )
# (451, 10, '23', '第一節 政黨之組織及活動', '政黨以黨員大會為最高權力機關。黨員大會每學期應以至少召開一次為原則。 <br><br>政黨代表由黨員大會依章程規定選出。 <br><br>)
# (452, 10, '24', '第一節 政黨之組織及活動', '政黨各大決議以政黨章程規範之。 )
# (453, 10, '25', '第二節 政黨之財務', '政黨之經費及收入，其來源如下： <br><br>一、黨費。 <br><br>二、政黨補助金。 <br><br>三、其他合法所得。 <br><br>)
# (454, 10, '26', '第二節 政黨之財務', '主管機關對於每屆全校不分區學生議員選舉得票率達百分之五以上之政黨，應編列年度預算補助之。 <br><br>前項補助，應由主管機關依當屆全校不分區學生議員選舉得票率依比例核算補助金額，通知政黨於十四天內掣據向主管機關領取。政黨未於規定期限內領取補助者，主管機關應催告其於一個月內具領；屆時未領取者，視為放棄。 <br><br>政黨依前項規定領取之補助，應用於競選費用、人事費用、政策研究費用及人才培育費用。 )