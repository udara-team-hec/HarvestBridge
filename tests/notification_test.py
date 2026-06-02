import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv(override=True)

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
MY_NUMBER=os.getenv("MY_NUMBER")

client = Client(ACCOUNT_SID, AUTH_TOKEN)

message = client.messages.create(
    from_=f"whatsapp:{TWILIO_NUMBER}",  # this is always the Twilio sandbox number
    to=f'whatsapp:{MY_NUMBER}',
    body=(
        "🌾 HarvestBridge Test\n\n"
        "If you are reading this, the notification pipeline is working.\n\n"
        "💰 Fair Price: ₦38,000 – ₦42,000 per tonne\n"
        "🚫 Floor Price: Do not accept below ₦34,000\n"
        "📈 Leverage: Global cassava demand is up 6% this quarter\n\n"
        "This is a test from Week 1 of the build."
    )
)

print(f"Message sent. SID: {message.sid}")
print("Check your WhatsApp now.")