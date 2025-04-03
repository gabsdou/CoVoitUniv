import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def envoyer_email(sujet, corps, expediteur, destinataire, mot_de_passe):
    # Créer un objet MIMEMultipart
    msg = MIMEMultipart()
    msg['From'] = expediteur
    msg['To'] = destinataire
    msg['Subject'] = sujet

    # Attacher le corps de l'e-mail à l'objet MIMEMultipart
    msg.attach(MIMEText(corps, 'plain'))

    try:
        # Connexion au serveur SMTP de Gmail
        serveur = smtplib.SMTP('smtp.gmail.com', 587)
        serveur.starttls()  # Sécuriser la connexion
        serveur.login(expediteur, mot_de_passe)
        texte = msg.as_string()
        serveur.sendmail(expediteur, destinataire, texte)
        print("E-mail envoyé avec succès!")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        serveur.quit()

# Exemple d'utilisation
sujet = "Sujet de l'e-mail"
corps = "Ceci est le contenu de l'e-mail."
expediteur = "noreplycovoitbot@gmail.com"
destinataire = "denislinde5@gmail.com"
mot_de_passe = "jrgm luus ckes zbzc"

envoyer_email(sujet, corps, expediteur, destinataire, mot_de_passe)
