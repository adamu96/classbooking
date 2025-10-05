import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_gmail(subject, message):
    """Sends an email using Gmail."""
    sender_email = "adam.urquhart96@gmail.com"  # Replace with your Gmail address
    sender_password = "qnis tauw zcev kroe"  # Replace with your App Password

    try:
        msg = MIMEMultipart()
        msg['From'] = "adam.urquhart96@gmail.com"
        msg['To'] = "adam.urquhart96@gmail.com; margretbarclay10@gmail.com"
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))  # Use 'html' for HTML messages

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Email sent successfully!")

    except Exception as e:
        print(f"Error sending email: {e}")

if __name__ == '__main__':
    send_gmail('test', 'test')