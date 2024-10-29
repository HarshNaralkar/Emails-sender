import streamlit as st
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

# CSS styling
st.markdown("""
    <style>
    .main-content {
        padding: 30px;
        background-color: #1e1e2e;
        border-radius: 12px;
        color: #ffffff;
    }
    .stExpander {
        color: white; /* Default color */
    }
    .stExpander:hover {
        color: green; /* Change color on hover */
    }
    .stButton>button {
        background-color: #246af7;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 18px;
        transition: color 0.3s ease; /* Smooth transition */
    }
    .stButton>button:hover {
        color: #00ff00; /* Change text color to green on hover */
    }
    .recipient-table {
        width: 100%;
        margin-top: 20px;
        border-collapse: collapse;
    }
    .recipient-table th, .recipient-table td {
        padding: 10px;
        border: 1px solid #ccc;
        text-align: left;
    }
    .recipient-table input, .recipient-table .stFileUploader {
        width: 100%;
        font-size: 14px;
    }        
    </style>
""", unsafe_allow_html=True)

st.title("📧 Dynamic Email Sender with Individualized Attachments")

# Section for sender email and message details
with st.container():
    st.markdown("### 📝 Fill in the Email Details")
    sender_email = st.text_input("Your Email", placeholder="you@example.com")
    password = st.text_input("Password", type="password", placeholder="Your password")

    with st.expander("📹 Password Creation Guide"):
        st.markdown(
            """
             <iframe width="560" height="315" src="https://www.youtube.com/embed/Ar340gxwhTs?si=F4p_ZvYtID4zVBim" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
             """,
            unsafe_allow_html=True
        )
    col1 , col2 , col3 = st.columns(3)
    with col3:
        # Send Test Email button
        test_send_button = st.button("📬 Send Test Email")
    st.write("---")
    # Function to send test email
    def send_test_email(sender_email, password):
        try:
            # Email setup
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = sender_email  # Send to self
            message['Subject'] = "Test Email From Quick Mail Sender."
            message.attach(MIMEText("This is a test email to verify your credentials.", 'plain'))

            # SMTP server configuration and email sending
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, sender_email, message.as_string())

            st.success("✅ Email and password are working correctly! Test email sent successfully.")
        except Exception as e:
            st.error(f"❌ Failed to send test email: {e}")

    if test_send_button:
        send_test_email(sender_email, password)

subject = st.text_input("Email Subject", placeholder="Enter the email subject")
message_body = st.text_area("Message Body", placeholder="Type your message here...")
st.write("---")
# Table-like structure for recipient emails and file selection
st.markdown("### 📋 Enter Recipients and Select Attachments")

# User-defined number of rows for recipient email and file attachment entries
num_recipients = st.number_input("Number of Recipients", min_value=1, step=1, value=1)

# Creating two lists to store recipient emails and attachments
recipient_emails = []
attachments = []

# Create table structure
st.markdown("<table class='recipient-table'><tr><th>Recipient Email</th><th>Attachment(s)</th></tr>", unsafe_allow_html=True)
for i in range(num_recipients):
    col1, col2 = st.columns([3, 2])
    with col1:
        email = st.text_input(f"Recipient Email {i+1}", key=f"email_{i}", placeholder="Recipient email")
        recipient_emails.append(email)
    with col2:
        file = st.file_uploader(f"Attachment {i+1}", key=f"file_{i}", type=["pdf", "jpg", "png", "docx"], accept_multiple_files=True)
        attachments.append(file)
st.markdown("</table>", unsafe_allow_html=True)

# Send Emails button
submit_button = st.button("📨 Send Emails")

# Function to send emails
def send_emails(sender_email, password, recipient_emails, subject, body, attachments):
    success_count, failure_count = 0, 0
    results = []

    for email, attachment_files in zip(recipient_emails, attachments):
        if not email:
            st.warning("Please enter all recipient emails.")
            return results, success_count, failure_count
        if not attachment_files:
            st.warning("Please attach files for all recipients.")
            return results, success_count, failure_count

        try:
            # Email setup
            message = MIMEMultipart()
            message['From'] = sender_email
            message['To'] = email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))

            # Attach multiple files
            for attachment_file in attachment_files:
                attachment_file.seek(0)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment_file.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment_file.name)}')
                message.attach(part)

            # SMTP server configuration and email sending
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(sender_email, password)
                server.sendmail(sender_email, email, message.as_string())

            results.append(f"✅ Email sent successfully to {email}")
            success_count += 1

        except Exception as e:
            results.append(f"❌ Failed to send email to {email}: {e}")
            failure_count += 1

    return results, success_count, failure_count

# Handle email sending when button is clicked
if submit_button:
    with st.spinner("⏳ Sending emails..."):
        results, success_count, failure_count = send_emails(sender_email, password, recipient_emails, subject, message_body, attachments)

    # Display results
    with st.expander("📋 Email Sending Results"):
        for result in results:
            st.write(result)
        st.write(f"✅ {success_count} emails sent successfully.")
        st.write(f"❌ {failure_count} emails failed.")
