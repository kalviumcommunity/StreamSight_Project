"""
Export Scheduler - Automates scheduled report generation and delivery

Runs reports on defined schedules and handles error notifications
to ensure stakeholders always have the latest insights.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Callable, Any
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class ExportScheduler:
    """Schedule and automate report generation."""

    def __init__(self):
        """Initialize scheduler."""
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
        self._load_jobs_config()

    def _load_jobs_config(self):
        """Load scheduled jobs from configuration."""
        config_path = Path("export") / "schedule_config.json"
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.jobs = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load jobs config: {str(e)}")

    def schedule_daily(
        self,
        job_name: str,
        job_func: Callable,
        hour: int = 9,
        minute: int = 0,
        **kwargs
    ):
        """
        Schedule a job to run daily.

        Args:
            job_name: Unique job identifier
            job_func: Function to call
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            **kwargs: Arguments to pass to job_func
        """
        self.scheduler.add_job(
            job_func,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=f"{job_name}_daily",
            name=f"{job_name} (Daily)",
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(f"Scheduled daily job: {job_name} at {hour:02d}:{minute:02d}")

    def schedule_weekly(
        self,
        job_name: str,
        job_func: Callable,
        day_of_week: str = "mon",
        hour: int = 9,
        minute: int = 0,
        **kwargs
    ):
        """
        Schedule a job to run weekly.

        Args:
            job_name: Unique job identifier
            job_func: Function to call
            day_of_week: Day to run (mon-sun)
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            **kwargs: Arguments to pass to job_func
        """
        self.scheduler.add_job(
            job_func,
            trigger=CronTrigger(
                day_of_week=day_of_week,
                hour=hour,
                minute=minute
            ),
            id=f"{job_name}_weekly",
            name=f"{job_name} (Weekly)",
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(
            f"Scheduled weekly job: {job_name} on {day_of_week} at {hour:02d}:{minute:02d}"
        )

    def schedule_monthly(
        self,
        job_name: str,
        job_func: Callable,
        day_of_month: int = 1,
        hour: int = 9,
        minute: int = 0,
        **kwargs
    ):
        """
        Schedule a job to run monthly.

        Args:
            job_name: Unique job identifier
            job_func: Function to call
            day_of_month: Day of month to run (1-31)
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            **kwargs: Arguments to pass to job_func
        """
        self.scheduler.add_job(
            job_func,
            trigger=CronTrigger(
                day=day_of_month,
                hour=hour,
                minute=minute
            ),
            id=f"{job_name}_monthly",
            name=f"{job_name} (Monthly)",
            kwargs=kwargs,
            replace_existing=True
        )
        logger.info(
            f"Scheduled monthly job: {job_name} on day {day_of_month} at {hour:02d}:{minute:02d}"
        )

    def start(self):
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Export scheduler started")

    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Export scheduler stopped")

    def list_jobs(self) -> list:
        """Get list of scheduled jobs."""
        return self.scheduler.get_jobs()

    def remove_job(self, job_name: str):
        """Remove a scheduled job."""
        try:
            self.scheduler.remove_job(job_name)
            logger.info(f"Removed job: {job_name}")
        except Exception as e:
            logger.error(f"Failed to remove job {job_name}: {str(e)}")
