import os
import sqlite3
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from src.agents.price_agent import analyze_price
from src.notifications.whatsapp import send_whatsapp_alert, build_alert_message


DB_PATH = os.getenv("DB_PATH", "data/harvestbridge.db")


def check_and_notify():
    """
    Runs every 24 hours.
    Checks each registered farmer's crop price.
    Fires WhatsApp alert if price trend changed.
    """
    print(f"[Scheduler] Running price check at {datetime.now()}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, phone_number, crop, region, country,
               currency, quantity_kg, price_threshold_pct
        FROM farmers_registry
    """)
    farmers = cursor.fetchall()

    if not farmers:
        print("[Scheduler] No registered farmers.")
        conn.close()
        return

    for farmer in farmers:
        (farmer_id, name, phone, crop, region, country,
         currency, quantity_kg, threshold_pct) = farmer

        try:
            price_data = analyze_price(
                crop=crop,
                region=region,
                currency=currency,
                country=country
            )

            avg_price = price_data.get("avg_price", 0)
            trend     = price_data.get("trend_direction")
            trend_val = trend.value if hasattr(trend, "value") else str(trend)

            # Derive change pct from trend direction
            if trend_val == "Rising":
                change_pct    = threshold_pct + 1
                harvest_urgency = "Medium"
            elif trend_val == "Falling":
                change_pct    = -(threshold_pct + 1)
                harvest_urgency = "High"
            else:
                change_pct    = 0
                harvest_urgency = "Low"

            # Only alert if price moved beyond threshold
            if abs(change_pct) > threshold_pct:
                message = build_alert_message(
                    crop=crop,
                    region=region,
                    current_price=avg_price,
                    currency=currency,
                    change_pct=change_pct,
                    harvest_urgency=harvest_urgency
                )
                sent = send_whatsapp_alert(to_number=phone, message=message)

                if sent:
                    cursor.execute("""
                        UPDATE farmers_registry
                        SET last_notified_at = ?
                        WHERE id = ?
                    """, (datetime.now(timezone.utc).isoformat(), farmer_id))
                    conn.commit()
                    print(f"[Scheduler] Alert sent to {name} ({phone})")
            else:
                print(f"[Scheduler] No alert for {name} — price stable")

        except Exception as e:
            print(f"[Scheduler] Error processing {name}: {e}")

    conn.close()
    print("[Scheduler] Check complete.")


def start_scheduler():
    """Starts the background scheduler. Called once from main.py."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        check_and_notify,
        trigger="interval",
        hours=24,
        next_run_time=datetime.now()
    )
    scheduler.start()
    print("[Scheduler] Background scheduler started — running every 24 hours.")
    return scheduler