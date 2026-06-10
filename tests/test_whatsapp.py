import os
from dotenv import load_dotenv
load_dotenv(override=True)
from src.notifications.whatsapp import send_whatsapp

result = send_whatsapp(
    to_number=f"{os.getenv('YOUR_PHONE_NUMBER')}",  # replace with your actual number
    message="HarvestBridge test message - notifications working"
)
print("Sent:", result)