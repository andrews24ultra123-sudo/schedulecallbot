async def main():
    print("Bot started at", datetime.now(TZ))

    scheduler = AsyncIOScheduler(timezone=TZ)

    # === TUESDAY JOBS ===
    # Every Tuesday 18:02 (6:02 PM) SGT -> /cgpoll
    scheduler.add_job(
        job_cgpoll,
        CronTrigger(day_of_week="tue", hour=18, minute=2),
        name="Tuesday 6:02pm CG Poll"
    )

    # Every Tuesday 18:04 (6:04 PM) SGT -> /sunpoll
    scheduler.add_job(
        job_sunpoll,
        CronTrigger(day_of_week="tue", hour=18, minute=4),
        name="Tuesday 6:04pm Sun Poll"
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
