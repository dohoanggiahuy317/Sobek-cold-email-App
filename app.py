from flask import Flask, request, render_template, jsonify, send_file, session, redirect, url_for
import pandas as pd, io, re, gspread, smtplib, os
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart

import script.utils.util as util
import script.utils.constant as constant

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'change-this')
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

@app.route('/send_preview', methods=['POST'])
def send_preview():
    # get form data
    name = request.form['recipient_name']
    email = request.form['recipient_email']
    company = request.form['recipient_company']
    subject = request.form['subject']
    body = request.form['body']
    # save data in session for final send
    session['preview'] = {
        'recipient': {'name': name, 'email': email, 'company': company},
        'subject': subject,
        'body': body
    }
    # handle attachments
    files = request.files.getlist('attachments')
    attachment_names = []
    for f in files:
        path = os.path.join('uploads', f.filename)
        f.save(path)
        attachment_names.append(f.filename)
    session['preview']['attachments'] = attachment_names
    return render_template('preview.html', preview=session['preview'])


@app.route('/send_email', methods=['POST'])
def send_final():
    preview = session.pop('preview', None)
    if not preview:
        return redirect(url_for('index'))
    # call existing send logic
    util.send_email(
        sender=os.environ['SMTP_USER'],
        password=os.environ['SMTP_PASS'],
        recipient_email=preview['recipient']['email'],
        subject=preview['subject'],
        body=preview['body'],
        attachments=[os.path.join('uploads', fn) for fn in preview.get('attachments', [])]
    )
    # redirect or show success
    return render_template('sent.html', recipient=preview['recipient'])


# ==============================================================================
# ==================================== PART 3 ==================================
# ==============================================================================

@app.route('/api/recipients', methods=['GET'])
def get_recipients():
    """Return the full list of recipients from the last preview."""
    data = util.recipient_df.to_dict(orient='records')
    return jsonify(data)






if __name__ == '__main__':
    app.run(debug=True)