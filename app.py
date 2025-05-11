from flask import Flask, request, render_template, jsonify, send_file, session, redirect, url_for
import pandas as pd, io, re, gspread, smtplib, os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
import json

import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import script.utils.util as util
import script.utils.constant as constant

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)  # opens browser for consent
    return build('gmail', 'v1', credentials=creds)

def send_message(service, user_id, message):
    return service.users().messages().send(userId=user_id, body=message).execute()

def create_message(to, subject, body_text):
    msg = MIMEText(body_text)
    msg['to'] = to
    msg['subject'] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

# Load SMTP credentials from JSON file
creds_path = os.path.join('credentials', 'your_email_info_here')
with open(creds_path) as f:
    SMTP_CREDS = json.load(f)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this')
gc = gspread.service_account(filename='credentials.json')


# ==============================================================================
# ==================================== PART 1 ==================================
# ==============================================================================


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/preview', methods=['POST'])
def preview():
    """
    Preview the data from the uploaded file or Google Sheets URL.
    """
    try:
        data = request.form.to_dict()
        df = util.get_preview_data(data, gc)
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        return jsonify(error=str(e)), 400


# ==============================================================================
# ==================================== PART 2 ==================================
# ==============================================================================

@app.route('/mail_template', methods=['GET'])
def get_template():
    """
    Return the default email template as plain text.
    """
    
    if not os.path.exists(constant.template_path):
        return jsonify(error="Template not found"), 404
    return send_file(constant.template_path, mimetype='text/plain')

@app.route('/upload_template', methods=['POST'])
def upload_template():
    """
    Save uploaded or edited template to disk.
    """
    
    try:
        return util.upload_template()
    except Exception as e:
        return jsonify(error=str(e)), 400
    

@app.route('/save_template', methods=['POST'])
def save_template():
    """
    Save uploaded or edited template to disk.
    """
    
    try:
        return util.save_template()
    except Exception as e:
        return jsonify(error=str(e)), 400

# Gmail helper functions
def get_gmail_service():
    flow = InstalledAppFlow.from_client_secrets_file('client_secret_91971590783-frl5oh8g80u7kgsaprh2mpa1ho9o8p9f.apps.googleusercontent.com.json', SCOPES)
    creds = flow.run_local_server(port=0)
    return build('gmail', 'v1', credentials=creds)

def create_message(to, subject, body_text):
    msg = MIMEText(body_text)
    msg['to'] = to
    msg['subject'] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {'raw': raw}

# ==============================================================================
# ==================================== PART 3 ==================================
# ==============================================================================


@app.route('/recipients', methods=['GET'])
def get_recipients():
    """Return the full list of recipients from the last preview."""
    data = util.recipient_df.to_dict(orient='records')
    return jsonify(data)


@app.route('/send_email', methods=['POST'])
def send_email():
    data = request.get_json() or {}
    rec = data.get('recipient', {})
    subject = data.get('subject', '')
    body = data.get('body', '')
    # Initialize Gmail service
    service = get_gmail_service()
    # Create and send message
    message = create_message(rec.get('email'), subject, body)
    sent = service.users().messages().send(userId='me', body=message).execute()
    return jsonify(status='sent', messageId=sent.get('id'))




if __name__ == '__main__':
    app.run(debug=True)