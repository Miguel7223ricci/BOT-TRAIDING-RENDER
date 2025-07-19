import os
from dotenv import load_dotenv
from twilio.rest import Client

load_dotenv()

def enviar_whatsapp(mensaje):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_whatsapp_number = 'whatsapp:+14155238886'
    to_whatsapp_number = os.getenv("TO_WHATSAPP")

    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=mensaje,
        from_=from_whatsapp_number,
        to=to_whatsapp_number
    )
    print(f"✅ WhatsApp enviado. SID: {message.sid}")

