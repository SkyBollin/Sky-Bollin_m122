import json
import os
import smtplib
import ssl
from datetime import datetime
from email.header import Header
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr

import matplotlib.pyplot as plt
import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()
url = os.getenv('URL')
gmail_username=os.getenv('EMAIL_USERNAME')
gmail_password = os.getenv('EMAIL_PASSWORD')
send_to = os.getenv('EMAIL_DESTINATION')
email_text = os.getenv('EMAIL_TEXT')
subject = os.getenv('EMAIL_SUBJECT')

stocks_to_get = json.loads(os.getenv('STOCK_TO_GET'))
querystring = json.loads(os.getenv('QUERY'))
headers = json.loads(os.getenv('HEADERS'))

fileNameDate = datetime.today().strftime('%Y-%m-%d') + ".pdf"

dataHandle = []

def fetchData():
    for stock in stocks_to_get:
        querystring['symbol'] = stock
        try:
            response = requests.request("GET", url, headers=headers, params=querystring)
            if (response.status_code >= 300):
                exit(1)
            dataHandle.append(response.json())
        except Exception as e:
            print("ERROR! response:" + response)
            print(e)
            exit(1)

def parseData():
    for i in range(len(dataHandle)):
        dataHandle[i] = dataHandle[i]['Time Series (Daily)']
        df = pd.DataFrame(dataHandle[i]).sort_index()
        dataHandle[i] = df.transpose()[::-1]['1. open'].astype(float)

def plotGraph():
    fig1 = plt.figure()
    ax1 = fig1.add_subplot()

    for i in range(len(dataHandle)):
        ax1.plot(dataHandle[i])

    #fig, host = plt.subplots()
    #host.set_xlabel("Datum")
    #host.set_ylabel("Wert")
    #for i in range(len(dataHandle)):
    #    client = host.twinx()
    #    c, = client.plot(dataHandle[i], label=stocks_to_get[i])
    #fig.tight_layout()

def saveGraph():
    plt.savefig(fileNameDate, format='pdf')

def sendEmail():
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()

    msg = MIMEMultipart('alternative')
    msg['From'] = formataddr((str(Header('Weekly Stock Market', 'utf-8')), 'umfrage.ny.test@gmail.com'))
    html = "email contents"
    msg.attach(MIMEText(html, 'html'))
    msg.attach(MIMEApplication(open(fileNameDate, encoding='unicode_escape').read(),_subtype="pdf"))
    server.sendmail('umfrage.ny.test@gmail.com', 'asuzas.hogog@gmail.com', msg.as_string())
    
    server.close()

def start():
    fetchData()
    parseData()
    plotGraph()
    saveGraph()
    #sendEmail()
    
def log(toLog):
    print(toLog)

start()
