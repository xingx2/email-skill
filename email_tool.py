#!/usr/bin/env python3
import argparse
import smtplib
import imaplib
import email
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import decode_header

# Configuration from Environment Variables or Hardcoded Defaults
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.163.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))
IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.163.com")
EMAIL_USER = os.environ.get("EMAIL_USER", "housizai1998@163.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "KAiRi3B9c3SHWzf8")

import mimetypes
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

def send_email(to_addr, subject, body, attachments=None):
    """Sends an email via SMTP."""
    print(f"DEBUG: Starting send_email to {to_addr}")
    if not EMAIL_USER or not EMAIL_PASS:
        print("Error: EMAIL_USER and EMAIL_PASS environment variables must be set.")
        sys.exit(1)

    print(f"DEBUG: Configured SMTP Server: {SMTP_SERVER}:{SMTP_PORT}")
    print(f"DEBUG: User: {EMAIL_USER}")

    msg = MIMEMultipart()
    msg['From'] = email.utils.formataddr(('Sender', EMAIL_USER))
    msg['To'] = email.utils.formataddr(('Recipient', to_addr))
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Handle Attachments
    if attachments:
        for file_path in attachments:
            print(f"DEBUG: Processing attachment: {file_path}")
            try:
                if not os.path.exists(file_path):
                    print(f"Error: Attachment not found at {file_path}")
                    continue

                ctype, encoding = mimetypes.guess_type(file_path)
                if ctype is None or encoding is not None:
                    # No guess could be made, or the file is encoded (compressed), so
                    # use a generic bag-of-bits type.
                    ctype = 'application/octet-stream'
                
                maintype, subtype = ctype.split('/', 1)
                
                with open(file_path, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(file_path)

                    if maintype == 'text':
                        # Note: we should handle calculating the charset
                        att = MIMEText(file_data.decode('utf-8'), _subtype=subtype)
                    elif maintype == 'image':
                        att = MIMEImage(file_data, _subtype=subtype)
                    else:
                        att = MIMEBase(maintype, subtype)
                        att.set_payload(file_data)
                        encoders.encode_base64(att)
                    
                    att.add_header('Content-Disposition', 'attachment', filename=file_name)
                    msg.attach(att)
                    print(f"DEBUG: Attached {file_name}")
            except Exception as e:
                print(f"Error attaching file {file_path}: {e}")
                sys.exit(1)

    try:
        if SMTP_PORT == 465:
            print("DEBUG: Connecting to SMTP_SSL...")
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            print("DEBUG: Connecting to SMTP...")
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            print("DEBUG: Starting TLS...")
            server.starttls()
            
        # server.set_debuglevel(True) # Verbose SMTP logs if needed
        print("DEBUG: Logging in...")
        server.login(EMAIL_USER, EMAIL_PASS)
        
        print("DEBUG: Sending email...")
        text = msg.as_string()
        server.sendmail(EMAIL_USER, to_addr, text)
        
        print("DEBUG: Quitting server...")
        server.quit()
        print(f"Successfully sent email to {to_addr}")
    except Exception as e:
        print(f"Error sending email: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def read_emails(limit=5):
    """Reads the latest N emails from the Inbox."""
    print(f"DEBUG: Starting read_emails limit={limit}")
    if not EMAIL_USER or not EMAIL_PASS:
        print("Error: EMAIL_USER and EMAIL_PASS environment variables must be set.")
        sys.exit(1)

    print(f"DEBUG: Configured IMAP Server: {IMAP_SERVER}")
    print(f"DEBUG: User: {EMAIL_USER}")

    try:
        # print("DEBUG: Connecting to IMAP_SSL...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        
        # print("DEBUG: Logging in...")
        mail.login(EMAIL_USER, EMAIL_PASS)

        # 163 requires IMAP ID before SELECT
        imaplib.Commands['ID'] = ('AUTH',)
        mail._simple_command('ID', '("name" "python" "version" "1.0")')

        # print("DEBUG: Selecting Inbox...")
        status, count = mail.select("INBOX")
        if status != "OK":
            print(f"Error: Failed to select INBOX: {count}")
            sys.exit(1)
        print(f"DEBUG: INBOX selected, {count[0].decode()} messages")

        # print("DEBUG: Searching for unread emails...")
        status, messages = mail.search(None, "UNSEEN")
        email_ids = messages[0].split()
        # print(f"DEBUG: Found {len(email_ids)} unread emails.")

        if not email_ids:
            print("DEBUG: No unread emails found. Note: If you opened the email in another client, it is no longer 'UNSEEN'.")
            return
        
        # Get latest N emails
        latest_email_ids = email_ids[-limit:]
        latest_email_ids.reverse() # Newest first

        # print(f"Fetching latest {len(latest_email_ids)} emails...\n")

        for i, e_id in enumerate(latest_email_ids):
            print(f"DEBUG: Fetching email {i+1}/{len(latest_email_ids)} (ID: {e_id.decode()})...")
            status, msg_data = mail.fetch(e_id, "(RFC822)")
            # Explicitly mark as seen (though fetch usually does this)
            mail.store(e_id, '+FLAGS', '\\Seen')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    # Decode From
                    from_ = msg.get("From")
                    
                    print(f"[{i+1}] From: {from_}")
                    print(f"    Subject: {subject}")
                    
                    # Simple body extraction (text/plain preference)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                try:
                                    body = part.get_payload(decode=True).decode()
                                    break # Found text body
                                except: pass
                    else:
                        try:
                            body = msg.get_payload(decode=True).decode()
                        except: pass
                    
                    preview = body.strip().replace("\n", " ")[:100]
                    print(f"    Preview: {preview}...")
                    print("-" * 40)

        print("DEBUG: Logging out...")
        mail.logout()
    except Exception as e:
        print(f"Error reading emails: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Python Email Tool (IMAP/SMTP)")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Send command
    send_parser = subparsers.add_parser("send", help="Send an email")
    send_parser.add_argument("to", help="Recipient email address")
    send_parser.add_argument("subject", help="Email subject")
    send_parser.add_argument("body", help="Email body content")
    send_parser.add_argument("--attachments", nargs='*', help="List of file paths to attach")

    # Read command
    read_parser = subparsers.add_parser("read", help="Read recent emails")
    read_parser.add_argument("--limit", type=int, default=5, help="Number of emails to fetch (default: 5)")

    args = parser.parse_args()

    if args.command == "send":
        send_email(args.to, args.subject, args.body, args.attachments)
    elif args.command == "read":
        read_emails(args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
