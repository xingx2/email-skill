---
name: email
description: Send and read emails via Python SMTP/IMAP CLI tool
type: script
---

# Email Skill

Send and read emails using a Python CLI tool over SMTP and IMAP.

## Run

```bash
{pythonBin} {baseDir}/scripts/email_tool.py <command> [options]
```

## Workflow

When the user wants to **send** an email:

1. **Check whether the recipient is an email address or a person's name.**
   - If the recipient is already a valid email address (e.g. `someone@example.com`), skip to step 2.
   - If the recipient is a person's name (e.g. "张三", "李四"), you MUST first call `contactManageTool` with `{"command":"query"}` to search for that person. Extract the `email` field from the query result. If no email is found, inform the user that the contact has no email on file and stop.
2. Use the resolved email address to run the send command below.

## Commands

### Send an email

```bash
{pythonBin} {baseDir}/scripts/email_tool.py send "recipient@example.com" "Subject line" "Body text"
```

With attachments:

```bash
{pythonBin} {baseDir}/scripts/email_tool.py send "recipient@example.com" "Subject" "Body" --attachments "/path/to/file1.pdf" "/path/to/file2.docx"
```

### Read emails

```bash
{pythonBin} {baseDir}/scripts/email_tool.py read
{pythonBin} {baseDir}/scripts/email_tool.py read --limit 10
```

## Parameters

### send

| Parameter | Position | Required | Description |
|-----------|----------|----------|-------------|
| to | 1st arg | yes | Recipient email address |
| subject | 2nd arg | yes | Email subject line |
| body | 3rd arg | yes | Email body content |
| --attachments | flag | no | One or more file paths to attach |

### read

| Parameter | Flag | Required | Description |
|-----------|------|----------|-------------|
| --limit | flag | no | Number of emails to fetch (default: 5) |

## Important

- When the user specifies a recipient by **name** instead of email address, you **MUST** call `contactManageTool` with `{"command":"query"}` first to look up the email. Never guess or fabricate an email address.
- If multiple contacts match the name, list them and ask the user to confirm which one.
- If the contact has no email field, inform the user and do not proceed with sending.

## Output

- `send`: prints success/failure message with delivery status
- `read`: prints email list with sender, subject, and date
