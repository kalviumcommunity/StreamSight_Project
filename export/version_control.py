"""
Version Control - Tracks report versions and export history

Maintains timestamped records of all exports for:
- Audit trails
- Comparing reports across time
- Rollback/recovery
- Export success monitoring
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class VersionControl:
    """Track version history of exported reports."""

    def __init__(self, base_dir: Path):
        """
        Initialize version control.

        Args:
            base_dir: Base directory for exports
        """
        self.base_dir = Path(base_dir)
        self.history_file = self.base_dir / "export_history.json"
        self.history = self._load_history()

    def _load_history(self) -> Dict[str, Any]:
        """Load export history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load history: {str(e)}")
                return {}
        return {}

    def _save_history(self):
        """Save export history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {str(e)}")

    def track_export(
        self,
        report_name: str,
        timestamp: str,
        file_paths: Dict[str, str]
    ):
        """
        Track a new export.

        Args:
            report_name: Name of the report
            timestamp: Timestamp of export (YYYY-MM-DD_HHMMSS format)
            file_paths: Dictionary of file type -> path
        """
        if report_name not in self.history:
            self.history[report_name] = []

        entry = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "files": file_paths,
            "status": "success"
        }

        self.history[report_name].append(entry)
        self._save_history()
        logger.info(f"Tracked export: {report_name} @ {timestamp}")

    def track_error(
        self,
        report_name: str,
        error_message: str,
        timestamp: Optional[str] = None
    ):
        """
        Track an export error.

        Args:
            report_name: Name of the report
            error_message: Error message
            timestamp: Optional timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

        if report_name not in self.history:
            self.history[report_name] = []

        entry = {
            "timestamp": timestamp,
            "datetime": datetime.now().isoformat(),
            "status": "error",
            "error": error_message
        }

        self.history[report_name].append(entry)
        self._save_history()
        logger.info(f"Tracked error: {report_name} @ {timestamp}")

    def get_report_history(self, report_name: str) -> Dict[str, Any]:
        """
        Get version history for a specific report.

        Args:
            report_name: Name of the report

        Returns:
            Dictionary with report history
        """
        if report_name not in self.history:
            return {
                "report_name": report_name,
                "versions": [],
                "total_exports": 0,
                "successful_exports": 0,
                "failed_exports": 0
            }

        entries = self.history[report_name]
        successful = [e for e in entries if e.get('status') == 'success']
        failed = [e for e in entries if e.get('status') == 'error']

        return {
            "report_name": report_name,
            "versions": entries,
            "total_exports": len(entries),
            "successful_exports": len(successful),
            "failed_exports": len(failed),
            "latest": entries[-1] if entries else None
        }

    def get_latest_export(self, report_name: str) -> Dict[str, Any]:
        """
        Get the latest successful export for a report.

        Args:
            report_name: Name of the report

        Returns:
            Latest export entry, or None if not found
        """
        if report_name not in self.history:
            return None

        entries = self.history[report_name]
        successful = [e for e in entries if e.get('status') == 'success']

        return successful[-1] if successful else None

    def get_all_reports(self) -> List[str]:
        """Get list of all tracked reports."""
        return list(self.history.keys())

    def get_exports_since(
        self,
        report_name: str,
        days_ago: int
    ) -> List[Dict[str, Any]]:
        """
        Get exports since a certain date.

        Args:
            report_name: Name of the report
            days_ago: Number of days back to search

        Returns:
            List of exports within timeframe
        """
        if report_name not in self.history:
            return []

        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = cutoff.replace(day=cutoff.day - days_ago)

        filtered = []
        for entry in self.history[report_name]:
            try:
                entry_date = datetime.fromisoformat(entry['datetime'])
                if entry_date >= cutoff:
                    filtered.append(entry)
            except Exception as e:
                logger.warning(f"Failed to parse date: {str(e)}")

        return filtered

    def generate_export_report(self) -> str:
        """
        Generate a summary report of all exports.

        Returns:
            Formatted text report
        """
        report = "EXPORT HISTORY SUMMARY\n"
        report += "=" * 50 + "\n\n"

        for report_name in self.get_all_reports():
            history = self.get_report_history(report_name)
            report += f"{report_name}\n"
            report += f"  Total Exports: {history['total_exports']}\n"
            report += f"  Successful: {history['successful_exports']}\n"
            report += f"  Failed: {history['failed_exports']}\n"

            if history['latest']:
                latest = history['latest']
                report += f"  Latest: {latest['timestamp']} ({latest['status']})\n"

            report += "\n"

        return report

    def cleanup_old_exports(self, days_to_keep: int = 30) -> int:
        """
        Remove export directory entries older than specified days.

        Args:
            days_to_keep: Number of days to keep

        Returns:
            Number of directories removed
        """
        cutoff = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        cutoff = cutoff.replace(day=cutoff.day - days_to_keep)

        removed_count = 0

        for report_dir in self.base_dir.glob("*/"):
            if report_dir.is_dir() and report_dir.name != 'logs':
                for version_dir in report_dir.glob("*/"):
                    if version_dir.is_dir():
                        try:
                            # Parse timestamp from directory name
                            timestamp_str = version_dir.name
                            version_date = datetime.strptime(
                                timestamp_str,
                                "%Y-%m-%d_%H%M%S"
                            )

                            if version_date < cutoff:
                                import shutil
                                shutil.rmtree(version_dir)
                                logger.info(f"Cleaned up: {version_dir}")
                                removed_count += 1
                        except Exception as e:
                            logger.warning(f"Failed to cleanup {version_dir}: {str(e)}")

        logger.info(f"Cleanup complete: {removed_count} directories removed")
        return removed_count
