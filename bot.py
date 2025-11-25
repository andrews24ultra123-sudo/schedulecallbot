import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# === HARD-CODED CONFIG ===

TOKEN = "8259780420:AAFxiZbMhnYfgCcwhselQiCTRKodZaZnooU"
DEFAULT_CHAT_ID = -1001819726736

API_BASE = f"https://api.telegram.org/bot{TOKEN}"
TZ = ZoneInfo("Asia/Singapore")


async def send_message(text: str):
    """
    Send a text message to the Telegram group.
    """
    url = f"{API_BASE}/sendMessage"
    payload = {
        "chat_id": DEFAULT_CHAT_ID,
        "text": text,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, data=payload, timeout=10)
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
    print("Bot starting up at", datetime.now(TZ))

    scheduler = AsyncIOScheduler(timezone=TZ)

    # Every Friday at 23:00 (11 PM) Asia/Singapore
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="fri", hour=23, minute=0),
        name="Friday CG Poll"
    )

    # Every Sunday at 14:00 (2 PM) Asia/Singapore
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
