# Suppose this is in email_utils.py or somewhere in your codebase
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

  # Use your Gmail address and password (stored securely or in environment variables)
SENDER_EMAIL = "noreplycovoitbot@gmail.com"
SENDER_PASSWORD = "jrgm luus ckes zbzc"

def send_email_via_gmail(sender_email, sender_password, to_email, subject, body):
    """
    Sends an email using Gmail's SMTP server.
    """
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the plain text body
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}. Error: {e}")


def send_offer_email(driver, passenger, departure_hour, sender_email, sender_password):
    """
    Composes and sends an email to the passenger when a driver offers them a ride.
    """
    # 1) Build the subject
    subject = "Nouvelle Offre de Covoiturage - Confirmation Requise"

    # 2) Build the body text
    driver_name = f"{driver.first_name} {driver.last_name}"
    departure_time = departure_hour.strftime("%d/%m/%Y à %H:%M")

    body = (
        f"Bonjour {passenger.first_name} {passenger.last_name},\n\n"

        f"Nous avons le plaisir de vous informer que {driver_name} vous propose un trajet en covoiturage.\n"
        f"Détails du trajet :\n"
        f"- Heure de départ : {departure_time}\n"
        f"- Conducteur : {driver_name}\n\n"
        f"Pour accepter ou refuser cette offre, veuillez vous connecter à l'application CoVoitUniv.\n\n"
        f"Si vous avez des questions ou besoin d'assistance, n'hésitez pas à nous contacter.\n\n"
        f"Cordialement,\n\n"
        f"L'équipe CoVoitUniv\n"
        f"Contact : supportcovoitbot@gmail.com\n"
    )

    # 3) Send it off!
    send_email_via_gmail(
        sender_email=sender_email,
        sender_password=sender_password,
        to_email=passenger.email,
        subject=subject,
        body=body
    )

# Example usage

