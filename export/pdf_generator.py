"""
PDF Generator - Converts markdown and HTML to PDF reports

Generates professional PDF reports from markdown content.
Suitable for email distribution and stakeholder presentations.
"""

import logging
from pathlib import Path
from typing import Optional
import markdown
from html import escape

logger = logging.getLogger(__name__)


class PDFGenerator:
    """Generate PDF reports from markdown content."""

    def __init__(self):
        """Initialize PDF generator."""
        self._check_dependencies()

    @staticmethod
    def _check_dependencies():
        """Check if required dependencies are available."""
        try:
            import weasyprint  # noqa
        except ImportError:
            logger.warning(
                "WeasyPrint not installed. PDF generation will be skipped. "
                "Install with: pip install weasyprint"
            )

    def generate_from_markdown(
        self,
        markdown_content: str,
        output_path: Path,
        title: str = "Report",
        include_toc: bool = False
    ) -> bool:
        """
        Generate PDF from markdown content.

        Args:
            markdown_content: Markdown text to convert
            output_path: Path where PDF will be saved
            title: Report title for PDF metadata
            include_toc: Whether to include table of contents

        Returns:
            True if successful, False otherwise
        """
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            logger.warning("WeasyPrint not installed. Skipping PDF generation.")
            return False

        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(
                markdown_content,
                extensions=['tables', 'fenced_code', 'codehilite']
            )

            # Wrap with styling
            html_document = self._create_styled_html(html_content, title)

            # Generate PDF
            HTML(string=html_document).write_pdf(str(output_path))
            logger.info(f"PDF generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return False

    def generate_from_html(
        self,
        html_content: str,
        output_path: Path,
        title: str = "Report"
    ) -> bool:
        """
        Generate PDF from HTML content.

        Args:
            html_content: HTML string
            output_path: Path where PDF will be saved
            title: Report title

        Returns:
            True if successful, False otherwise
        """
        try:
            from weasyprint import HTML
        except ImportError:
            logger.warning("WeasyPrint not installed. Skipping PDF generation.")
            return False

        try:
            # Wrap with styling
            html_document = self._create_styled_html(html_content, title)

            # Generate PDF
            HTML(string=html_document).write_pdf(str(output_path))
            logger.info(f"PDF generated: {output_path}")
            return True

        except Exception as e:
            logger.error(f"PDF generation failed: {str(e)}")
            return False

    @staticmethod
    def _create_styled_html(content: str, title: str) -> str:
        """Create styled HTML document for PDF."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{escape(title)}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    margin: 20px;
                    background-color: #fff;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #1a5490;
                    margin-top: 20px;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }}
                h1 {{
                    font-size: 28px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin: 15px 0;
                }}
                table, th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                blockquote {{
                    border-left: 4px solid #1a5490;
                    margin: 15px 0;
                    padding-left: 15px;
                    color: #555;
                }}
                img {{
                    max-width: 100%;
                    height: auto;
                }}
                .metadata {{
                    font-size: 12px;
                    color: #999;
                    margin-top: 20px;
                    padding-top: 10px;
                    border-top: 1px solid #eee;
                }}
            </style>
        </head>
        <body>
            {content}
            <div class="metadata">
                <p>Report generated automatically. For questions, contact the analytics team.</p>
            </div>
        </body>
        </html>
        """
