import imaplib
import email
import pandas as pd

from pathlib import Path
from email.utils import parsedate_to_datetime

# =====================================
# IMPORT CREDENTIALS
# =====================================

from my_details import (
    GMAIL_USER,
    GMAIL_PASS
)


# =====================================
# CONFIGURATION
# =====================================

EMAIL_ADDRESS = GMAIL_USER
APP_PASSWORD = GMAIL_PASS

IMAP_SERVER = "imap.gmail.com"

SENDER_FILTER = "noreply@lendenclub.com"

CSV_FILE = "lenden_cashflow.csv"

# =====================================
# CREATE CSV IF NOT EXISTS
# =====================================

if not Path(CSV_FILE).exists():

    df = pd.DataFrame(columns=[
        "Fund_as_on",
        "DayNAme",
        "Deposit",
        "Total_Amt",
        "Fee_6%",
        "Int_Recvd",
        "PA_Recvd",
        "PA_+_Int",
        "Bal_end_of_the_Day"
    ])

    df.to_csv(
        CSV_FILE,
        index=False
    )

    print("Created:", CSV_FILE)

# =====================================
# LOGIN TO GMAIL
# =====================================

mail = imaplib.IMAP4_SSL(IMAP_SERVER)

mail.login(
    EMAIL_ADDRESS,
    APP_PASSWORD
)

mail.select("INBOX")

print("Gmail Login Successful")

# =====================================
# FETCH ONLY UNREAD EMAILS
# =====================================

status, messages = mail.search(
    None,
    '(UNSEEN FROM "noreply@lendenclub.com")'
)

from email.header import decode_header

def decode_email_subject(subject):

    decoded_parts = decode_header(subject)

    decoded_subject = ""

    for part, encoding in decoded_parts:

        if isinstance(part, bytes):

            decoded_subject += part.decode(
                encoding or "utf-8",
                errors="ignore"
            )

        else:
            decoded_subject += part

    return decoded_subject


email_ids = messages[0].split()

print(
    f"Unread Emails Found: {len(email_ids)}"
)

# ==========================================
# SEARCH ONLY LENDEN EMAILS
# ==========================================

status, messages = mail.search(
    None,
    '(UNSEEN FROM "noreply@lendenclub.com")'
)

email_ids = messages[0].split()

filtered_email_ids = []

for email_id in email_ids:

    status, data = mail.fetch(
        email_id,
        "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])"
    )

    header_data = data[0][1].decode(
        "utf-8",
        errors="ignore"
    )

    subject = decode_email_subject(
        header_data.replace("Subject:", "").strip()
    )

    subject_lower = subject.lower()

    if (
        "credited to your lendenclub account".lower()
        in subject_lower
        or
        "has been processed to your bank account".lower()
        in subject_lower
    ):
        filtered_email_ids.append(email_id)

email_ids = filtered_email_ids

print(
    f"Matching Emails Found: {len(email_ids)}"
)

# =====================================
# PROCESS EMAILS
# =====================================

for email_id in email_ids:

    try:

        status, data = mail.fetch(
            email_id,
            "(BODY.PEEK[])"
        )

        raw_email = data[0][1]

        msg = email.message_from_bytes(
            raw_email
        )

        sender = msg.get(
            "From",
            ""
        )

        if SENDER_FILTER.lower() not in sender.lower():

            continue

        subject = msg.get(
            "Subject",
            ""
        )

        email_date = msg.get(
            "Date",
            ""
        )

        txn_dt = parsedate_to_datetime(
            email_date
        )

        fund_date = txn_dt.strftime(
            "%d-%m-%Y"
        )

        day_name = txn_dt.strftime(
            "%A"
        )

        print(
            fund_date,
            day_name,
            subject
        )

        # Future:
        # Parse deposit emails
        # Parse repayment emails
        # Update CSV

    except Exception as e:

        print(
            f"ERROR: {e}"
        )

# =====================================
# CLEANUP
# =====================================

mail.logout()

from pathlib import Path

print(
    "CSV Path:",
    Path(CSV_FILE).resolve()
)

print(
    "\nCompleted Successfully."
)

print(
    fund_date,
    day_name,
    subject
)

subject = decode_email_subject(subject)

body = ""

if msg.is_multipart():

    for part in msg.walk():

        content_type = part.get_content_type()

        try:

            payload = part.get_payload(
                decode=True
            )

            if payload:

                text = payload.decode(
                    part.get_content_charset() or "utf-8",
                    errors="ignore"
                )

                if content_type == "text/plain":

                    body = text
                    break

                elif content_type == "text/html" and not body:

                    body = text

        except:
            pass

else:

    try:

        body = msg.get_payload(
            decode=True
        ).decode(
            msg.get_content_charset() or "utf-8",
            errors="ignore"
        )

    except:
        pass

print("\n" + "=" * 80)
print(subject)
print("=" * 80)
print(body[:5000])
print("=" * 80)

with open(
    "debug_email.html",
    "w",
    encoding="utf-8"
) as f:

    f.write(body)

print(
    "\nSaved HTML to:",
    Path("debug_email.html").resolve()
)

from bs4 import BeautifulSoup

soup = BeautifulSoup(body, "html.parser")

text = soup.get_text(
    separator="\n",
    strip=True
)

print("\n" + "=" * 80)
print(text[:5000])
print("=" * 80)