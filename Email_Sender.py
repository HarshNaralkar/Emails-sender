import streamlit as st
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import List
import os

# CSS styling for buttons and layout
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .main-content {
        padding: 20px;
        background-color: #f4f4f9;
        border-radius: 8px;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

st.title("📧 Send Email with Specific Attachments")

# Email form inputs
with st.form("email_form"):
    st.markdown("## Enter Email Details")
    sender_email = st.text_input("Your Email")
    password = st.text_input("Password", type="password")
    subject = st.text_input("Subject")
    body = st.text_area("Message Body")

    email_list = st.text_area("Enter recipient emails, each on a new line", placeholder="example1@gmail.com\nexample2@gmail.com")

    attachments = st.file_uploader("Upload all necessary files (up to 1 GB total)", accept_multiple_files=True, type=["pdf", "jpg", "png", "docx"])
    submit_button = st.form_submit_button("Send Emails")

def send_emails(sender_email: str, password: str, emails: List[str], subject: str, body: str, attachments):
    success_count = 0
    failure_count = 0
    results = []

    # Check total attachment size
    total_size = sum([file.size for file in attachments])
    max_size = 1 * 1024 * 1024 * 1024  # 1 GB limit
    if total_size > max_size:
        st.error(f"Total attachment size exceeds 1 GB limit. Total: {total_size / (1024 * 1024):.2f} MB")
        return [], 0, len(emails)

    # Organize files by their names (without extension)
    files_dict = {os.path.splitext(file.name)[0]: file for file in attachments}

    # Process each recipient
    for email in emails:
        email_with_prefix = email.strip()  # Full email including domain
        email_prefix = email_with_prefix.split('@')[0]  # Extract prefix from email

        # Check if the full email name matches any of the file names (excluding extension)
        if email_with_prefix in files_dict:
            try:
                # Email setup
                message = MIMEMultipart()
                message['From'] = sender_email
                message['To'] = email_with_prefix
                message['Subject'] = subject
                message.attach(MIMEText(body, 'plain'))

                # Attach the specific file for this email
                file = files_dict[email_with_prefix]
                file.seek(0)  # Reset file pointer
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file.name)}')
                message.attach(part)

                # Connect to SMTP server and send email
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(sender_email, password)
                    server.sendmail(sender_email, email_with_prefix, message.as_string())

                results.append(f"✅ Email sent successfully to {email_with_prefix}")
                success_count += 1

            except Exception as e:
                results.append(f"❌ Failed to send email to {email_with_prefix}: {e}")
                failure_count += 1
        else:
            results.append(f"❌ No attachment found for {email_with_prefix} matching filename '{email_with_prefix}'")
            failure_count += 1

    return results, success_count, failure_count

# Send email on form submission
if submit_button:
    # Parse emails into a list
    emails = [email.strip() for email in email_list.splitlines() if email.strip()]

    # Show loading spinner
    with st.spinner("Sending emails..."):
        results, success_count, failure_count = send_emails(sender_email, password, emails, subject, body, attachments)

    # Display results in an expander
    with st.expander("Email Sending Results"):
        for result in results:
            st.write(result)
        st.write(f"✅ {success_count} emails sent successfully. ❌ {failure_count} emails failed.")
