#!/usr/bin/env python3
"""Quick test: verify IMAP read access works."""
import imaplib
import os
import sys

IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.163.com")
EMAIL_USER = os.environ.get("EMAIL_USER", "housizai1998@163.com")
EMAIL_PASS = os.environ.get("EMAIL_PASS", "KAiRi3B9c3SHWzf8")

try:
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)

    imaplib.Commands['ID'] = ('AUTH',)
    mail._simple_command('ID', '("name" "python" "version" "1.0")')

    status, count = mail.select("INBOX")
    if status != "OK":
        print(f"FAIL: select INBOX failed: {count}")
        sys.exit(1)

    total = int(count[0])
    status, messages = mail.search(None, "UNSEEN")
    unread = len(messages[0].split()) if messages[0] else 0

    mail.logout()
    print(f"OK: IMAP login success. Inbox: {total} total, {unread} unread.")
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
