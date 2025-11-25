import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# === FULLY HARD-CODED CONFIG ===

TOKEN = "8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU"
CHAT_ID = -1001819726736

# Fully hardcoded API URL for sendMessage
API_URL_SEND_MESSAGE = "https://api.telegram.org/bot8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU/sendMessage"

TZ = ZoneInfo("Asia/Singapore")


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
            if resp.status_code != 200:
                print("Failed to send message:", resp.status_code, resp.text)
            else:
                print(f"Sent message at {datetime.now(TZ)}: {text}")
        except Exception as e:
            print("Error sending message:", e)


async def job_cgpoll():
    await send_message("/cgpoll")


async def job_sunpoll():
    await send_message("/sunpoll")


async def main():
    print("Bot started at", datetime.now(TZ))

    scheduler = AsyncIOScheduler(timezone=TZ)

    # === WEDNESDAY JOBS ===
    # Every Wednesday 17:55 (5:55 PM) SGT -> /cgpoll
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="wed", hour=17, minute=55),
        name="Wednesday 5:55pm CG Poll"
    )

    # Every Wednesday 17:57 (5:57 PM) SGT -> /sunpoll
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="wed", hour=17, minute=57),
        name="Wednesday 5:57pm Sun Poll"
    )

    # === FRIDAY JOB ===
    # Every Friday 23:00 (11 PM) SGT -> /cgpoll
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="fri", hour=23, minute=0),
        name="Friday 11pm CG Poll"
    )

    # === SUNDAY JOB ===
    # Every Sunday 14:00 (2 PM) SGT -> /sunpoll
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="sun", hour=14, minute=0),
        name="Sunday 2pm Sun Poll"
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
