import os
from dotenv import load_dotenv
load_dotenv(override=True)

from src.notifications.whatsapp import send_whatsapp_alert, build_alert_message


def test_send_whatsapp():
    """Live test — sends a real message to your sandbox phone."""

    your_number = os.getenv("YOUR_PHONE_NUMBER")
    assert your_number, "Add YOUR_PHONE_NUMBER=+234... to your .env file"

    message = build_alert_message(
        crop="Maize",
        region="Kano",
        current_price=892.50,
        currency="NGN",
        change_pct=12.3,
        harvest_urgency="Low"
    )

    result = send_whatsapp_alert(
        to_number=your_number,
        message=message
    )

    assert result is True
    print("✓ WhatsApp alert sent and received")


if __name__ == "__main__":
    test_send_whatsapp()