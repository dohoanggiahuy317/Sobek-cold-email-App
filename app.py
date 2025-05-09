from flask import Flask, request, render_template, jsonify, send_file
import pandas as pd, io, re, gspread, smtplib, os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

import script.utils.util as util
import script.utils.constant as constant

app = Flask(__name__)
gc = gspread.service_account(filename='credentials.json')


# ==============================================================================
# ==================================== PART 1 ==================================
# ==============================================================================


@app.route('/', methods=['GET','POST'])
def index():
    return render_template('index.html')


@app.route('/api/preview', methods=['POST'])
def preview():
    """
    Preview the data from the uploaded file or Google Sheets URL.
    """
    try:
        data = request.form.to_dict()
        df = util.get_preview_data(data, gc)
        return jsonify(df.head(10).to_dict(orient='records'))
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

@app.route('/mail_template', methods=['POST'])
def upload_template():
    """
    Save uploaded or edited template to disk.
    """
    
    try:
        return util.upload_template()
    except Exception as e:
        return jsonify(error=str(e)), 400

# ==============================================================================
# ==================================== PART 3 ==================================
# ==============================================================================

# @app.route('/api/send_email', methods=['POST'])
# def send_email_api():
#     """
#     Sends a single email with optional attachments.
#     Expects JSON: {
#       "recipient": {"name": ..., "email": ..., "company": ...},
#       "subject": "...",
#       "body": "...",
#       "attachments": ["path1", ...]  # optional
#     }
#     """
#     data = request.get_json()
#     sender = os.environ.get('SMTP_USER')
#     password = os.environ.get('SMTP_PASS')
#     rec = data['recipient']
#     subject = data['subject']
#     body = data['body']
#     attachments = data.get('attachments', [])
#     # Build message
#     msg = MIMEMultipart()
#     msg['From'] = sender
#     msg['To'] = rec['email']
#     msg['Subject'] = subject
#     msg.attach(MIMEText(body, 'plain'))
#     for file_path in attachments:
#         part = MIMEBase("application", "octet-stream")
#         with open(file_path, "rb") as f:
#             part.set_payload(f.read())
#         encoders.encode_base64(part)
#         part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
#         msg.attach(part)
#     # Send
#     server = smtplib.SMTP(os.environ.get('SMTP_HOST','smtp.gmail.com'), 587)
#     server.starttls()
#     server.login(sender, password)
#     server.sendmail(sender, rec['email'], msg.as_string())
#     server.quit()
#     return jsonify(status="sent")

# @app.route('/api/upload_attachments', methods=['POST'])
# def upload_attachments():
#     files = request.files.getlist('attachments')
#     saved = []
#     for f in files:
#         path = os.path.join('uploads', f.filename)
#         f.save(path)
#         saved.append(path)
#     return jsonify(saved)





if __name__ == '__main__':
    app.run(debug=True)