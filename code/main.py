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
querystring = json.loads(os.getenv('QUERY'))
headers = json.loads(os.getenv('HEADERS'))
fileNameDate = datetime.today().strftime('%Y-%m-%d') + ".pdf"

def fetchData():
    response = requests.request("GET", url, headers=headers, params=querystring)
    print(response)
    return response.json()

def parseData(data):
    df = pd.DataFrame(data["Time Series (Daily)"])
    df = df.transpose()[::-1]
    df = pd.to_numeric(df['1. open'])
    return df
    
def plotGraph(data):
    plot = data.plot.line()
    plot.set_xlabel('Datum')
    plot.set_ylabel('Aktienwert')
    plot.set_title('Aktienkurs von IBM')
    return plot.get_figure()

def saveGraph(line):
    line.savefig(fileNameDate, bbox_inches='tight', format='pdf')

def sendEmail():
    server = smtplib.SMTP_SSL('smtp.sendgrid.net', 465, context = ssl.create_default_context())
    server.ehlo()
    server.login("apikey", "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")

    msg = MIMEMultipart('alternative')
    msg['From'] = formataddr((str(Header('Weekly Stock Market', 'utf-8')), 'umfrage.ny.test@gmail.com'))
    html = "email contents"
    msg.attach(MIMEText(html, 'html'))
    msg.attach(MIMEApplication(open(fileNameDate, encoding='unicode_escape').read(),_subtype="pdf"))
    server.sendmail('umfrage.ny.test@gmail.com', 'asuzas.hogog@gmail.com', msg.as_string())
    
    server.close()


def start():
    data = fetchData()
    #data = parseData(data)
    #line = plotGraph(data)
    #saveGraph(line)
    #sendEmail()
    
def log(toLog):
    print(toLog)

start()
