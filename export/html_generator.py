"""
HTML Generator - Creates interactive HTML reports with embedded charts

Generates self-contained HTML files with:
- Markdown summary converted to HTML
- Embedded Plotly charts
- Data preview tables
- Professional styling
- Responsive design
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any
import pandas as pd
import markdown

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generate interactive HTML reports with charts."""

    def __init__(self):
        """Initialize HTML generator."""
        pass

    def generate_report(
        self,
        summary_text: str,
        charts_dict: Dict[str, Any],
        report_name: str,
        output_path: Path,
        data_preview: Optional[pd.DataFrame] = None
    ) -> Path:
        """
        Generate interactive HTML report.

        Args:
            summary_text: Markdown summary text
            charts_dict: Dictionary of chart name -> plotly figure
            report_name: Report title
            output_path: Where to save the HTML file
            data_preview: Optional DataFrame to preview

        Returns:
            Path to generated HTML file
        """
        try:
            # Convert markdown to HTML
            html_summary = markdown.markdown(
                summary_text,
                extensions=['tables', 'fenced_code', 'codehilite']
            )

            # Build HTML document
            html_content = self._create_html_document(
                report_name=report_name,
                summary_html=html_summary,
                charts_dict=charts_dict,
                data_preview=data_preview
            )

            # Write to file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logger.info(f"HTML report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"HTML generation failed: {str(e)}")
            raise

    def _create_html_document(
        self,
        report_name: str,
        summary_html: str,
        charts_dict: Dict[str, Any],
        data_preview: Optional[pd.DataFrame]
    ) -> str:
        """Create complete HTML document with styling."""
        
        # Build charts HTML
        charts_html = self._build_charts_section(charts_dict)
        
        # Build data preview HTML
        preview_html = self._build_data_preview_section(data_preview)

        html_document = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report_name} - Interactive Report</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                    min-height: 100vh;
                    padding: 20px;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 10px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                header {{
                    background: linear-gradient(135deg, #1a5490 0%, #2d7bb3 100%);
                    color: white;
                    padding: 40px 20px;
                    text-align: center;
                }}
                header h1 {{
                    font-size: 2.5em;
                    margin-bottom: 10px;
                }}
                header p {{
                    font-size: 1.1em;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px;
                }}
                .section {{
                    margin-bottom: 50px;
                    padding-bottom: 30px;
                    border-bottom: 2px solid #f0f0f0;
                }}
                .section:last-child {{
                    border-bottom: none;
                }}
                .section h2 {{
                    color: #1a5490;
                    font-size: 1.8em;
                    margin-bottom: 20px;
                    display: flex;
                    align-items: center;
                }}
                .section h2:before {{
                    content: "";
                    width: 4px;
                    height: 30px;
                    background: #1a5490;
                    margin-right: 15px;
                    border-radius: 2px;
                }}
                .chart-container {{
                    margin: 30px 0;
                    padding: 20px;
                    background: #f9f9f9;
                    border-radius: 8px;
                    border: 1px solid #eee;
                }}
                .chart-title {{
                    font-size: 1.3em;
                    font-weight: 600;
                    color: #333;
                    margin-bottom: 15px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                    font-size: 0.95em;
                }}
                table th {{
                    background-color: #f0f0f0;
                    color: #1a5490;
                    font-weight: 600;
                    padding: 12px;
                    text-align: left;
                    border-bottom: 2px solid #1a5490;
                }}
                table td {{
                    padding: 10px 12px;
                    border-bottom: 1px solid #eee;
                }}
                table tr:hover {{
                    background-color: #f9f9f9;
                }}
                .data-preview {{
                    background: #f9f9f9;
                    padding: 20px;
                    border-radius: 8px;
                    border: 1px solid #eee;
                }}
                .data-preview h3 {{
                    color: #1a5490;
                    margin-bottom: 15px;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.95em;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    overflow-x: auto;
                    border: 1px solid #ddd;
                }}
                blockquote {{
                    border-left: 4px solid #1a5490;
                    margin: 15px 0;
                    padding-left: 20px;
                    color: #666;
                    font-style: italic;
                }}
                footer {{
                    background: #f9f9f9;
                    padding: 20px;
                    text-align: center;
                    color: #666;
                    border-top: 1px solid #eee;
                    font-size: 0.9em;
                }}
                .nav {{
                    position: sticky;
                    top: 0;
                    background: white;
                    padding: 15px 40px;
                    border-bottom: 1px solid #eee;
                    display: flex;
                    gap: 20px;
                    z-index: 100;
                }}
                .nav a {{
                    color: #1a5490;
                    text-decoration: none;
                    font-weight: 500;
                    transition: color 0.3s;
                }}
                .nav a:hover {{
                    color: #2d7bb3;
                }}
                @media (max-width: 768px) {{
                    .container {{
                        border-radius: 0;
                    }}
                    header h1 {{
                        font-size: 1.8em;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                    .nav {{
                        flex-direction: column;
                        gap: 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>📊 {report_name}</h1>
                    <p>Interactive Analysis Report</p>
                </header>

                <nav class="nav">
                    <a href="#summary">Summary</a>
                    <a href="#visualizations">Visualizations</a>
                    {f'<a href="#data">Data Preview</a>' if data_preview is not None else ''}
                </nav>

                <div class="content">
                    <!-- Summary Section -->
                    <section class="section" id="summary">
                        <h2>Summary</h2>
                        {summary_html}
                    </section>

                    <!-- Visualizations Section -->
                    {charts_html}

                    <!-- Data Preview Section -->
                    {preview_html}
                </div>

                <footer>
                    <p>Report generated automatically • For questions, contact the analytics team</p>
                    <p style="font-size: 0.85em; margin-top: 10px;">
                        This report contains proprietary information. 
                        Do not share without authorization.
                    </p>
                </footer>
            </div>
        </body>
        </html>
        """

        return html_document

    def _build_charts_section(self, charts_dict: Dict[str, Any]) -> str:
        """Build HTML section with embedded charts."""
        if not charts_dict:
            return ""

        charts_html = '<section class="section" id="visualizations"><h2>Visualizations</h2>'

        for chart_name, chart_figure in charts_dict.items():
            try:
                if hasattr(chart_figure, 'to_html'):
                    # Plotly figure
                    chart_html = chart_figure.to_html(
                        include_plotlyjs=False,
                        div_id=f"chart_{chart_name.replace(' ', '_')}"
                    )
                    charts_html += f"""
                    <div class="chart-container">
                        <div class="chart-title">{chart_name}</div>
                        {chart_html}
                    </div>
                    """
                else:
                    logger.warning(f"Unsupported chart type for: {chart_name}")
            except Exception as e:
                logger.error(f"Failed to embed chart '{chart_name}': {str(e)}")

        charts_html += '</section>'
        return charts_html

    def _build_data_preview_section(self, data_preview: Optional[pd.DataFrame]) -> str:
        """Build HTML section with data preview."""
        if data_preview is None or data_preview.empty:
            return ""

        html = '<section class="section" id="data"><h2>Data Preview</h2>'
        html += '<div class="data-preview">'
        html += f'<h3>Showing first {len(data_preview)} rows</h3>'
        html += data_preview.to_html(classes='preview-table', index=False)
        html += '</div></section>'

        return html
