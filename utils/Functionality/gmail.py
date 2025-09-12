import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_registration_email(user_email, user_name):
    
    receiver_email = user_email

    subject = "✅ Registrazione completata su Core Posture"

    plain_text = f"""
Ciao {user_name},

La tua registrazione su Core Posture è avvenuta con successo!

Email: {user_email}

Grazie per esserti unito a noi 💪

—
Il team di Core Posture
"""

    html = f"""
<html>
<head>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f9f9fb;
            padding: 20px;
        }}
        .container {{
            background-color: #ffffff;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            max-width: 600px;
            margin: auto;
            color: #333333;
        }}
        h2 {{
            color: #5e3ea1;
        }}
        p {{
            font-size: 16px;
        }}
        .footer {{
            font-size: 12px;
            color: #999999;
            margin-top: 30px;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2>🎉 Benvenuto su Core Posture!</h2>
        <p><strong>Nome utente:</strong> {user_name}</p>
        <p><strong>Email:</strong> {user_email}</p>
        <p>La tua registrazione è avvenuta con successo. Grazie per esserti unito alla nostra community dedicata al miglioramento della postura e del benessere!</p>
        <div class="footer">
            Questo messaggio è stato generato automaticamente. Non rispondere a questa email.
        </div>
    </div>
</body>
</html>
"""

    # Composizione del messaggio
    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject

    # Aggiunge sia plain text che HTML
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("Email HTML inviata con successo.")
    except Exception as e:
        print(f"Errore durante l'invio dell'email: {e}")
