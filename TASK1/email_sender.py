import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText



def send_email(to, subject, repository_name, author_name,date_at,title,id ):
    smtp_server=os.getenv("SMTP_SERVER")
    port=os.getenv("SMTP_PORT")
    login=os.getenv("SMTP_LOGIN")
    receiver=os.getenv("SMTP_RECIEVER")
    password=os.getenv("SMTP_PASSWORD")
    sender=os.getenv("SMTP_SENDER")

    html=rf"""<!DOCTYPE html>
        <html>
        <head>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body>
        <table width="100%" border="0" cellpadding="0" cellspacing="0" align="center" valign="top">
            <tr>
                <td align="center" style="padding: 10px 0 0 0; ">
                    <h1> {subject} </h1>
                </td>
            </tr>
            <tr>
                <td align="left" style="padding: 0 0 0 20px;">
                    <p> Details: </p>
                    <p> Author: <b>{author_name}</b> </p>
                    <p> Repository: <b>{repository_name}</b> </p>
                    <p> Date commit: <b>{date_at}</b> </p>
                    <p> Commit title: <b>{title}</b> </p>
                    <p> Commit ID: <b>{id}</b> </p>
                </td>
            </tr>
        </table>
        </body>
        </html>
"""

    message=MIMEMultipart()
    message['From'] = receiver
    message['To'] = to
    message['Subject'] = subject
    message.attach(MIMEText(html, 'html'))

    text=message.as_string()

    s=smtplib.SMTP(smtp_server, port)
    s.ehlo()
    s.starttls()
    s.login(login, password)  # Включить https://support.google.com/accounts/answer/6010255
    try:
        s.sendmail(sender, to, text.encode('utf-8'))
    except Exception as e:
        print(e)
