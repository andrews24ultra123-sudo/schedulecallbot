import asyncio
from datetime import datetime, timedelta

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

# === FULLY HARD-CODED CONFIG ===

TOKEN = "8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU"
CHAT_ID = -1001819726736

# Fully hardcoded API URL for sendMessage
API_URL_SEND_MESSAGE = (
    "https://api.telegram.org/"
    "bot8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU/sendMessage"
)


async def send_message(text: str):
    """
    Send a text message directly to the Telegram group.
    """
    if not text or text.strip() == "":
        print("ERROR — Attempted to send empty message. Skipped.")
        return

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(API_URL_SEND_MESSAGE, data=payload, timeout=10)
            print("DEBUG — Telegram response:", resp.status_code, resp.text)
            if resp.status_code != 200:
                print("Failed to send message:", resp.status_code, resp.text)
            else:
                print(f"Sent message at {datetime.utcnow()} UTC: {text}")
        except Exception as e:
            print("Error sending message:", e)


async def job_cgpoll():
    await send_message("/cgpoll")


async def job_sunpoll():
    await send_message("/sunpoll")


async def job_debug():
    # One-off debug message after deploy
    await send_message("Bot deployed OK ✅ (debug message)")


async def main():
    print("Bot started at (UTC):", datetime.utcnow())

    # Use UTC timezone to avoid any server tz issues
    scheduler = AsyncIOScheduler(timezone="UTC")

    # === ONE-OFF DEBUG MESSAGE ===
    # Fires 1 minute after the bot starts
    run_at = datetime.utcnow() + timedelta(minutes=1)
    scheduler.add_job(
        job_debug,
        DateTrigger(run_date=run_at),
        name="One-off debug message",
    )

    # === WEEKLY SCHEDULED JOBS (TIMES IN UTC) ===
    #
    # SGT is UTC+8, so:
    #   Tuesday 18:10 SGT -> Tuesday 10:10 UTC
    #   Tuesday 18:12 SGT -> Tuesday 10:12 UTC
    #   Friday 23:00 SGT  -> Friday 15:00 UTC
    #   Sunday 14:00 SGT  -> Sunday 06:00 UTC

    # Every Tuesday 10:10 UTC -> /cgpoll (6:10pm SGT)
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="tue", hour=10, minute=10),
        name="Tuesday 6:10pm SGT CG Poll",
    )

    # Every Tuesday 10:12 UTC -> /sunpoll (6:12pm SGT)
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="tue", hour=10, minute=12),
        name="Tuesday 6:12pm SGT Sun Poll",
    )

    # Every Friday 15:00 UTC -> /sunpoll (11:00pm SGT)
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="fri", hour=15, minute=0),
        name="Friday 11:00pm SGT Sun Poll",
    )

    # Every Sunday 06:00 UTC -> /cgpoll (2:00pm SGT)
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="sun", hour=6, minute=0),
        name="Sunday 2:00pm SGT CG Poll",
    )

    scheduler.start()

    # Keep alive
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
