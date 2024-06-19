import argparse
import json
from utils import fetch_data
from utils import send_mail

# Read information from the email_info file
mail = json.load(open("credentials/email_info.json"))
sender_email = mail["sender_email"]
sender_password = mail["sender_password"]
recipient_email = mail["recipient_email"]
attachments = mail["attachments"]

def read_email_template(file_path):
    """
    Reads an email template from a specified file and splits it into header and body.
    Args: 
        file_path (str): The path to the email template file.
    Returns: 
        tuple: A tuple containing the header (str) and the body (str) of the email template.
    """
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content into header and body
    parts = content.split("\n\n", 1)
    
    if len(parts) == 2:
        header = parts[0].strip()
        body = parts[1].strip()
    else:
        header = parts[0].strip()
        body = ""

    return header, body

def replace_placeholders(body, replace_text, info):
    """
    Replaces placeholders in the email body with actual information.
    Args:
        body (str): The body of the email template.
        replace_text (str): A comma-separated string of placeholders to replace.
        info (list): A list of strings with the information to replace the placeholders.
    Returns:
        str: The email body with placeholders replaced by the actual information.
    """
    replace_text = replace_text.split(",")
    for i in range(len(replace_text)):
        body = body.replace(replace_text[i], info[i])
    return body

def main():
    """
    Main function to send customized cold emails.

    This function parses command line arguments, retrieves data from a Google Sheets spreadsheet,
    reads an email template, replaces placeholders with actual data, and sends the emails.
    """
    parser = argparse.ArgumentParser(description='Sending Cold emails')
    parser.add_argument('--SAMPLE_SPREADSHEET_ID', help='SAMPLE_SPREADSHEET_ID')
    parser.add_argument('--SAMPLE_RANGE_NAME', help='SAMPLE_RANGE_NAME')
    parser.add_argument('--template_path', help='template_path')
    parser.add_argument('--replace_text', help='replace_text')
    args = parser.parse_args()

    # Get the data
    creds = fetch_data.get_credentials()
    data = fetch_data.retrieve_data(creds, args.SAMPLE_SPREADSHEET_ID, args.SAMPLE_RANGE_NAME)
    
    # Get the template
    header, body = read_email_template(args.template_path)
    print("\n---------------- This is the email you will send ----------------\n")
    print(body)
    print("-----------------------------------------------------------------\n")
    checkpoint = input("This is the email will look like.\nDo you want to start sending? [y/n]: ")

    if checkpoint.lower() != "y":
        print("Task stop")
        return

    # Start sending email for each person    
    for i in range(len(data)):
        name, company, recipient_email = data[i]
        
        # Get text for person
        person_body = replace_placeholders(body, args.replace_text, [name, company])

        # Preview
        print(f"\n---------------- Person {i + 1} Preview ----------------\n")
        print("MAIL TO:", recipient_email)
        print("TITLE:", header, "\n")
        print(person_body, "\n")
        print("Attachment:", attachments) if attachments else None
        print("---------------------------------------------------------\n")

        checkpoint = input("This is the email will look like.\nDo you want to start sending? [y/n]: ")
        if checkpoint.lower() == "y":
            print("Sending....")
            send_mail.send_email(sender_email, sender_password, recipient_email, header, person_body, attachments)
            print("Sent ✅")
        else:
            print("Next person")
            continue

    print("\nTask completed. Congratulations. 💯💯💯")

if __name__ == "__main__":
    main()
