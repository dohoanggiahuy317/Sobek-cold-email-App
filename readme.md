# Automate Cold Email Sending


## Overview
This project is designed to automate the process of sending personalized cold emails using data extracted from a Google Sheets spreadsheet. The script reads an email template, customizes it with specific information, and sends it to multiple recipients. The primary goal is to streamline the process of outreach, making it efficient and personalized.

## Problem
Sending cold emails manually can be a time-consuming and error-prone task, especially when dealing with a large number of recipients. It requires careful attention to detail to ensure each email is personalized and accurately sent to the right recipient. This manual process often leads to inconsistencies and inefficiencies.

## Solution
The solution involves automating the entire process of sending cold emails by:

- Retrieving data from a Google Sheets spreadsheet.
- Reading and customizing an email template.
- Sending personalized emails to each recipient based on the data.


## Tech Used
- Python: The primary programming language used for scripting and automation.
- Google Sheets API: For retrieving data from Google Sheets.
- smtplib: For sending emails via SMTP.
- email.mime: For constructing email messages.
- argparse: For handling command-line arguments.
- Challenges/Solutions
- Google Sheets API Authentication:

## Key Features
- Automated Data Retrieval: Automatically fetches recipient data from a specified Google Sheets spreadsheet.
- Template-Based Emailing: Uses a template for email content, ensuring consistency and ease of customization.
- Personalized Content: Dynamically inserts recipient-specific information into the email body.
- Attachment Support: Allows for including attachments in the emails.
- Command-Line Interface: Enables users to run the script with various options via command-line arguments.
- Easy keep track of emails you sending in real-time

Check point 1: Template email
<img width="661" alt="Screenshot 2024-06-19 at 11 25 40 PM" src="https://github.com/dohoanggiahuy317/Sobek-cold-email-App/assets/72744045/bd948468-4974-4b61-beac-70cf3bef0b2a">
Check point 2: Real email
<img width="659" alt="Screenshot 2024-06-19 at 11 25 59 PM" src="https://github.com/dohoanggiahuy317/Sobek-cold-email-App/assets/72744045/fcddd6ed-f0e9-4a22-964a-680ca1c24b9c">


## Impact and Results
This automation script significantly reduces the time and effort required to send personalized cold emails, enhancing productivity and ensuring consistency. It allows for large-scale email campaigns with minimal manual intervention, leading to more efficient outreach efforts and potentially higher response rates.

## How to Use

### 1. Setup and Installation:
- Ensure you have Python installed.
- Install required libraries using `pip install -r requirements.txt`.

### 2. Configuration:

- Follow Google Cloud instructions and save your your Google Sheets API credentials in a file named `credentials.json` under credentials.
- Prepare an `email_info.json` file with your email account details and recipient information:

```json
{
    "sender_email": "your_email@gmail.com",
    "sender_password": "your_password",
    "recipient_email": "recipient@example.com",
    "attachments": ["path/to/attachment1", "path/to/attachment2"]
}
```
- Prepare your email template file with placeholders such as [Name] and [Company].


### 3. Prepare Email Template
- The email template should be prepared in a text file (.txt) format.
- The first line of the text file should contain the email subject/header.
- The second line should be left empty.
- The rest of the file should contain the body of the email.

Example email:

```txt
Wanna Steal the Moon?

Dear [Name],

My name is Jeremy Do, Computer Science and Applied Mathematics @ Denison University. I really like Minions and I want to join your [Company] to steal the moon.

Can we schedule a brief 30-minute online meeting at your convenience?

Thank you very much for your time.
Best regards,
Jeremy Do

P.S.: I love bananas too.
```

### 4. Running the Script:

- Use the following command to run the script:

```bash
python your_script.py \
    --SAMPLE_SPREADSHEET_ID 'your_spreadsheet_id' \
    --SAMPLE_RANGE_NAME 'your_range_name' \
    --template_path 'path_to_template.txt' \
    --replace_text '[Name],[Company]'
```
- Seperate the text you want to replace using comma `,`.

### Author
Jeremy Do
