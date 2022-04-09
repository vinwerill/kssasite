import os
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from flask import Flask
app_host = 'http://kssasite.herokuapp.com'
app = Flask(__name__)
SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
dir = 'static/uploads/'
for data in os.listdir(dir):
	print("\ndata:"+os.path.join("static/uploads/", data)+"\n")
	# try:
	with open(os.path.join("static/uploads/", data), "rb") as fho:
		print(data.split(".")[1])
		attach = MIMEApplication(fho.read(), _subtype=data.split(".")[1])
	attach.add_header('Content-Disposition', 'attachment', filename=str(data))
	# except:
	# 	print(f"No such file '{data}'")
	# 	pass

def send_email(subject, embody, attachments=[], recipient='pyone.tw@gmail.com'):
                # flaskemail of google account
                sender = 'flask.pyone@gmail.com'
                password = 'yrqioxjnlkykjife'
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
                        # 附加 pdf 檔
                        for pdf in attachments:
                            try:
                                with open(pdf, "rb") as fho:
                                    the_pdf = MIMEApplication(fho.read(), _subtype="pdf")
                                the_pdf.add_header('Content-Disposition', 'attachment', filename=str(pdf))
                                content.attach(the_pdf)
                            except:
                                print(f"No such file '{pdf}'")
                                pass
                        smtp.send_message(content)
                    except Exception as e:
                        pass