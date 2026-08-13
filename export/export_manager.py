"""
Export Manager - Orchestrates multi-format exports of analysis results

Generates CSV, PDF, and HTML outputs in a single call.
Handles versioning, error tracking, and metadata generation.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import pandas as pd
import json

from .version_control import VersionControl
from .pdf_generator import PDFGenerator
from .html_generator import HTMLGenerator
from .email_delivery import EmailDelivery


logger = logging.getLogger(__name__)


class ExportManager:
    """Orchestrates multi-format export of analysis results."""

    def __init__(self, base_output_dir: str = "output"):
        """
        Initialize ExportManager.

        Args:
            base_output_dir: Root directory for all exports
        """
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        self.version_control = VersionControl(self.base_output_dir)
        self.pdf_generator = PDFGenerator()
        self.html_generator = HTMLGenerator()
        self.email_delivery = EmailDelivery()
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for export operations."""
        log_dir = self.base_output_dir / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"exports_{datetime.now().strftime('%Y%m%d')}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def export_analysis(
        self,
        df: pd.DataFrame,
        report_name: str,
        summary_text: str,
        charts_dict: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, str]] = None,
        data_dictionary: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        Export analysis in CSV, PDF, and HTML formats.

        Args:
            df: DataFrame containing analysis results
            report_name: Name of the report (used for filenames)
            summary_text: Summary text in markdown format
            charts_dict: Dictionary of chart name -> plotly figure
            metadata: Custom metadata to include (source, refresh date, etc.)
            data_dictionary: Column descriptions for data dictionary

        Returns:
            Dictionary with paths to generated files
            {
                'csv': '/path/to/data.csv',
                'pdf': '/path/to/report.pdf',
                'html': '/path/to/report.html',
                'metadata': '/path/to/metadata.json',
                'timestamp': '2024-01-15_143022'
            }
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            report_dir = self._create_report_directory(report_name, timestamp)
            
            logger.info(f"Starting export for report: {report_name}")
            
            # 1. Export CSV with metadata
            csv_path = self._export_csv(df, report_dir, data_dictionary)
            logger.info(f"CSV exported to: {csv_path}")
            
            # 2. Generate metadata
            metadata_path = self._generate_metadata(
                df, report_name, report_dir, metadata, data_dictionary
            )
            logger.info(f"Metadata generated: {metadata_path}")
            
            # 3. Generate PDF report
            pdf_path = self._export_pdf(
                summary_text, report_name, report_dir
            )
            if pdf_path:
                logger.info(f"PDF exported to: {pdf_path}")
            else:
                logger.warning("PDF generation skipped or failed")
            
            # 4. Generate HTML interactive report
            html_path = self._export_html(
                summary_text, charts_dict, report_name, report_dir, df
            )
            logger.info(f"HTML exported to: {html_path}")
            
            # 5. Create README for the report
            readme_path = self._create_readme(report_dir, report_name, timestamp)
            logger.info(f"README created: {readme_path}")
            
            # 6. Version control tracking
            self.version_control.track_export(
                report_name, timestamp, {
                    'csv': str(csv_path),
                    'pdf': str(pdf_path) if pdf_path else None,
                    'html': str(html_path),
                    'metadata': str(metadata_path),
                }
            )
            
            result = {
                'csv': str(csv_path),
                'pdf': str(pdf_path) if pdf_path else None,
                'html': str(html_path),
                'metadata': str(metadata_path),
                'readme': str(readme_path),
                'timestamp': timestamp,
                'report_dir': str(report_dir),
            }
            
            logger.info(f"Export completed successfully for {report_name}")
            return result
            
        except Exception as e:
            logger.error(f"Export failed for {report_name}: {str(e)}", exc_info=True)
            self._log_error_alert(report_name, str(e))
            raise

    def _create_report_directory(self, report_name: str, timestamp: str) -> Path:
        """Create timestamped report directory."""
        report_dir = (
            self.base_output_dir 
            / report_name 
            / timestamp
        )
        report_dir.mkdir(parents=True, exist_ok=True)
        return report_dir

    def _export_csv(
        self, 
        df: pd.DataFrame, 
        report_dir: Path,
        data_dictionary: Optional[Dict[str, str]] = None
    ) -> Path:
        """Export DataFrame to CSV with optional data dictionary."""
        csv_path = report_dir / "data.csv"
        df.to_csv(csv_path, index=False)
        
        # Export data dictionary if provided
        if data_dictionary:
            dict_path = report_dir / "data_dictionary.json"
            with open(dict_path, 'w') as f:
                json.dump(data_dictionary, f, indent=2)
        
        return csv_path

    def _generate_metadata(
        self,
        df: pd.DataFrame,
        report_name: str,
        report_dir: Path,
        metadata: Optional[Dict[str, str]] = None,
        data_dictionary: Optional[Dict[str, str]] = None
    ) -> Path:
        """Generate comprehensive metadata file."""
        meta = {
            "report_name": report_name,
            "generated_timestamp": datetime.now().isoformat(),
            "record_count": len(df),
            "column_count": len(df.columns),
            "columns": list(df.columns),
            "data_types": {col: str(df[col].dtype) for col in df.columns},
            "missing_values": {col: int(df[col].isna().sum()) for col in df.columns},
            "duplicate_rows": len(df[df.duplicated()]),
        }
        
        if metadata:
            meta.update(metadata)
        
        if data_dictionary:
            meta["data_dictionary"] = data_dictionary
        
        metadata_path = report_dir / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(meta, f, indent=2)
        
        return metadata_path

    def _export_pdf(
        self,
        summary_text: str,
        report_name: str,
        report_dir: Path
    ) -> Optional[Path]:
        """Generate PDF from markdown summary."""
        try:
            pdf_path = report_dir / "report.pdf"
            self.pdf_generator.generate_from_markdown(
                summary_text,
                pdf_path,
                title=report_name
            )
            return pdf_path
        except Exception as e:
            logger.warning(f"PDF generation failed: {str(e)}")
            return None

    def _export_html(
        self,
        summary_text: str,
        charts_dict: Optional[Dict[str, Any]],
        report_name: str,
        report_dir: Path,
        df: pd.DataFrame
    ) -> Path:
        """Generate interactive HTML report with charts."""
        html_path = report_dir / "report.html"
        self.html_generator.generate_report(
            summary_text=summary_text,
            charts_dict=charts_dict or {},
            report_name=report_name,
            output_path=html_path,
            data_preview=df.head(100)
        )
        return html_path

    def _create_readme(
        self,
        report_dir: Path,
        report_name: str,
        timestamp: str
    ) -> Path:
        """Create README with export information."""
        readme_path = report_dir / "README.md"
        
        content = f"""# {report_name} Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Timestamp: {timestamp}

## Files in this Report

- **data.csv** - Cleaned dataset in CSV format
- **metadata.json** - Report metadata and data schema
- **report.pdf** - Executive summary (PDF format)
- **report.html** - Interactive report with visualizations

## Using These Files

### CSV Dataset
Open `data.csv` in Excel or Python for further analysis.

### PDF Report
Print or email to stakeholders. Suitable for meetings and documentation.

### HTML Report
Open in web browser for interactive exploration of charts and findings.

## Data Dictionary
See `data_dictionary.json` (if included) for column descriptions.

## Questions?
Contact the data team for questions about this report.
"""
        
        with open(readme_path, 'w') as f:
            f.write(content)
        
        return readme_path

    def _log_error_alert(self, report_name: str, error_msg: str):
        """Log error alert for monitoring systems."""
        alert_file = self.base_output_dir / "logs" / "export_errors.log"
        with open(alert_file, 'a') as f:
            f.write(
                f"{datetime.now().isoformat()} | {report_name} | {error_msg}\n"
            )

    def get_report_history(self, report_name: str) -> Dict[str, Any]:
        """Get version history for a report."""
        return self.version_control.get_report_history(report_name)

    def send_report(
        self,
        export_result: Dict[str, str],
        recipient_email: str,
        subject: str,
        body: str,
        include_files: list = None
    ) -> bool:
        """
        Send generated report via email.

        Args:
            export_result: Result dict from export_analysis()
            recipient_email: Email address to send to
            subject: Email subject
            body: Email body text
            include_files: List of file types to include ('csv', 'pdf', 'html', 'metadata')

        Returns:
            True if sent successfully, False otherwise
        """
        if include_files is None:
            include_files = ['csv', 'html', 'metadata']
        
        try:
            attachments = []
            for file_type in include_files:
                if file_type in export_result and export_result[file_type]:
                    attachments.append(export_result[file_type])
            
            return self.email_delivery.send_report(
                recipient_email=recipient_email,
                subject=subject,
                body=body,
                attachments=attachments
            )
        except Exception as e:
            logger.error(f"Failed to send report: {str(e)}")
            return False
