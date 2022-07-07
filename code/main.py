import ftplib
import json
import logging
import os
import smtplib
from datetime import datetime
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('URL')
stocks_to_get = json.loads(os.getenv('STOCK_TO_GET'))
querystring = json.loads(os.getenv('QUERY'))
headers = json.loads(os.getenv('HEADERS'))

gmail_username=os.getenv('EMAIL_USERNAME')
gmail_password = os.getenv('EMAIL_PASSWORD')
email_text = os.getenv('EMAIL_TEXT')
email_subject = os.getenv('EMAIL_SUBJECT')
email_to = os.getenv('EMAIL_DESTINATION')

ftp_server = os.getenv('FTP_URL')
ftp_username = os.getenv('FTP_USERNAME')
ftp_password = os.getenv('FTP_PASSWORD')

fileNameDate = datetime.today().strftime('%Y-%m-%d') + ".pdf"
logging.basicConfig(filename=datetime.today().strftime('%Y-%m-%d') + ".log", level=logging.DEBUG)

dataHandle = []
data = {}

def fetch_Data():
    for stock in stocks_to_get:
        querystring['symbol'] = stock
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            if (response.status_code >= 300):
                exit(1)
            dataHandle.append(pd.DataFrame(response.json()['Time Series (Daily)']).iloc[0].transpose()[::-1].astype(float).to_frame().set_axis([stock], axis=1))
        except Exception as e:
            print("ERROR!")
            print(e)
            exit(1)

def plot_Graph():
    for i, dataRow in enumerate(dataHandle):
        if (i == 0):
            data = dataRow
            continue
        data = pd.concat([dataRow, data], axis=1)
    ax = data.sort_index().plot(title='Aktienverlauf')
    ax.set_xlabel('Datum')
    ax.set_ylabel('CHF')

def save_Graph():
    plt.savefig(fileNameDate)

def send_Email():
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(gmail_username, gmail_password)

            msg = MIMEMultipart('alternative')
            msg['From'] = formataddr((str(Header('Weekly Stock Market', 'utf-8')), gmail_username))
            msg['Subject'] = email_subject
            msg['To'] = email_to
            msg.attach(MIMEText(email_text, 'html'))
            with open(fileNameDate, 'rb') as pdf:
                attach = MIMEBase('application/pdf',"octet-stream")
                attach.set_payload(pdf.read())
            attach.add_header('Content-Disposition', 'attachment', filename=str(fileNameDate))
            msg.attach(attach)
            server.send_message(msg)
            
            server.close()
            log("Email sent successfully", 20)
    except Exception as e:
        log("EMAIL SENT FAILED", 40)
        log(e, 40)

def ftp_upload():
    try:
        with ftplib.FTP(ftp_server, ftp_username, ftp_password) as server:
            file = open(fileNameDate,'rb')
            server.storbinary(f'STOR {os.path.basename(fileNameDate)}', file)
            file.close()
            server.quit()
    except Exception as e:
        log("FTP UPLOAD FAILED", 40)
        log(e, 40)

def start():
    fetch_Data()
    plot_Graph()
    save_Graph()
    send_Email()
    ftp_upload()
    
def log(toLog, severity = 0):
    logging.log(severity, toLog)

start()
