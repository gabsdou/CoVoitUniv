# Suppose this is in email_utils.py or somewhere in your codebase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

  # Use your Gmail address and password (stored securely or in environment variables)
SENDER_EMAIL = "noreplycovoitbot@gmail.com"
SENDER_PASSWORD = "gabpizza"


def send_email_via_gmail(sender_email, sender_password, to_email, subject, body):
    """
    Sends an email using Gmail's SMTP server.
    """
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject

    # Attach the plain text body
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")


def send_offer_email(driver, passenger, sender_email, sender_password):
    """
    Composes and sends an email to the passenger when a driver offers them a ride.
    """
    # 1) Build the subject
    subject = "Nouvelle offre de covoiturage"

    # 2) Build the body text
    driver_name = f"{driver.first_name} {driver.last_name}"
    body = (
        f"Bonjour {passenger.first_name},\n\n"
        f"Vous avez reçu une nouvelle offre de la part de {driver_name}.\n"
        f"Veuillez vous connecter à l'application pour accepter ou refuser.\n\n"
        f"Cordialement,\n"
        f"L'équipe CoVoitUniv"
    )

    # 3) Send it off!
    send_email_via_gmail(
        sender_email=sender_email,
        sender_password=sender_password,
        to_email=passenger.email,
        subject=subject,
        body=body
    )