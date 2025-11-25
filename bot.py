import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# === FULLY HARD-CODED CONFIG ===

TOKEN = "8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU"
CHAT_ID = -1001819726736

# Fully hardcoded API base URL (no formatting)
API_URL_SEND_MESSAGE = "https://api.telegram.org/bot8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU/sendMessage"

TZ = ZoneInfo("Asia/Singapore")


async def send_message(text: str):
    """
    Send a text message directly to the Telegram group.
    """
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

    # Every Friday 11pm SGT
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="fri", hour=23, minute=0),
        name="Friday CG Poll"
    )

    # Every Sunday 2pm SGT
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="sun", hour=14, minute=0),
        name="Sunday Sun Poll"
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
