import pandas as pd, io, re, gspread, smtplib, os
from flask import Flask, request, render_template, jsonify, send_file
import script.utils.constant as constant

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
    
    # JSON body with edited template
    data = request.get_json(silent=True)
    if data and 'mail_template' in data:
        with open(constant.template_path, 'w') as wf:
            wf.write(data['mail_template'])
        return jsonify(success=True)
    return jsonify(error="No template provided"), 400