from typing import NoReturn

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from pkg.format_pkg import email_content
#https://www.learncodewithmike.com/2020/02/python-email.html
class email_sender():
    def __init__(self):
        self._sender = smtplib.SMTP(host="smtp.gmail.com", port="587")
        self._sender.ehlo()  # 驗證SMTP伺服器
        self._sender.starttls()  # 建立加密傳輸
        self._sender.login("hebearo777@gmail.com", 
                           "ogay irfm dzwc uqgl")  # 登入寄件者gmail
        self._email_content = {}

    def email_sending(self) -> NoReturn:
        ##The demo part could be find at functions.ipynb
        try:
            self._sender.send_message(self._email_content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)
            
    def set_content(self , subject:str='有漫畫更新囉 !!!',
                           to_:list[str] = ["asd094198@gmail.com"],
                           content:email_content=email_content)-> NoReturn:
        self._email_content = MIMEMultipart() 
        self._email_content["subject"] = subject  # 郵件標題
        self._email_content["from"] = 'hebearo777@gmail.com'  # 寄件者
        self._email_content["to"] = ','.join(to_)  # 收件者
        self._email_content.attach(MIMEText(content.get_html_content(),'html'))  # 郵件純文字內容
