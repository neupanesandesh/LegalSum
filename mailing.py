import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
load_dotenv()

GMAIL_APP_PASSWORD= os.getenv("GMAIL_APP_PASSWORD")
EMAIL_RECEIVER= os.getenv("EMAIL_RECEIVER")
EMAIL_SENDER= os.getenv("EMAIL_SENDER")


def send_email(api_key):
    YOUR_GOOGLE_EMAIL = EMAIL_SENDER
    YOUR_GOOGLE_EMAIL_APP_PASSWORD = GMAIL_APP_PASSWORD

    smtpserver = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtpserver.ehlo()
    smtpserver.login(YOUR_GOOGLE_EMAIL, YOUR_GOOGLE_EMAIL_APP_PASSWORD)

    # Construct the email
    msg = MIMEMultipart()
    msg['From'] = YOUR_GOOGLE_EMAIL
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = 'API Key error in Your app'

    # Email body
    body = f'''
    This is a predefined code from your Legal Summary NJ App, You are seeing this because your API key failed.\n
    Here is the key that failed:\n
    {api_key}
    
    '''
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    smtpserver.send_message(msg)

    # Close connection
    smtpserver.close()

