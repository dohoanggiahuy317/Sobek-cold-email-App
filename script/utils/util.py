import pandas as pd, io, re, gspread, smtplib, os
from flask import Flask, request, render_template, jsonify, send_file
import script.utils.constant as constant
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

# ==============================================================================
# ==================================== PART 1 ==================================
# ==============================================================================

recipient_df = pd.DataFrame(columns=['name','email','company'])

def extract_sheet_id(url):
    m = re.search(r'/d/([\w\-]+)', url)
    if not m:
        raise ValueError("Invalid Google Sheets URL")
    return m.group(1)


def get_preview_data(data, gc):
    """
    Reads all form fields into a dict (overwriting the data arg).
    Checks for an uploaded Excel file in request.files:
    If present, uses pandas.read_excel to load the specified sheet.
    Otherwise, extracts a Google Sheet ID from the submitted URL
    Looks for optional start_row and end_row values
    """
    global recipient_df

    data = request.form.to_dict()
   
    # priority to an uploaded file
    if 'file' in request.files and request.files['file'].filename:
        df = pd.read_excel(request.files['file'],
                           sheet_name=data['sheet_name'])
    
    else:
        sid = extract_sheet_id(data['url'])
        sh = gc.open_by_key(sid)
        sheet = sh.worksheet(data['sheet_name'])
        df = pd.DataFrame(sheet.get_all_records())
    
    # apply row range slicing if provided
    start = data.get('start_row')
    end = data.get('end_row')

    if not start:
        start = 2
    if not end:
        end = df.shape[0] + 1

    s = int(start)-2
    e = int(end)-1
    df = df.iloc[s:e]
    df = df[[data['name_col'], data['email_col'], data['company_col']]]
    df.columns = ['name','email','company']

    # save the recipient data to a global variable
    recipient_df = df.copy()

    return df


# ==============================================================================
# ==================================== PART 2 ==================================
# ==============================================================================

def upload_template():
    """Save uploaded or edited template to disk."""
    # File upload takes priority
    if 'file' in request.files and request.files['file'].filename:
        f = request.files['file']
        f.save(constant.template_path)
        return jsonify(success=True)

def save_template():
    # JSON body with edited template
    data = request.get_json(silent=True)
    if data and 'mail_template' in data:
        with open(constant.template_path, 'w') as wf:
            wf.write(data['mail_template'])
        return jsonify(success=True)
    return jsonify(error="No template provided"), 400


# ==============================================================================
# ==================================== PART 3 ==================================
# ==============================================================================


def send_email(sender_email, sender_password, recipient_email, subject, body, attachments=None):
    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Create a multipart message and set headers
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Add body to email
        msg.attach(MIMEText(body, 'plain'))

        # Attach files
        if attachments:
            for file in attachments:
                with open(file, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {os.path.basename(file)}",
                    )
                    msg.attach(part)

        # Convert message to string and send
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print("Email sent successfully.")
        server.quit()
    
    except Exception as e:
        print(f"Error: {e}")