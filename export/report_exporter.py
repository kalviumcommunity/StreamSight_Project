from pathlib import Path
import os
import json
import logging
from datetime import datetime

try:
    import markdown
except Exception:
    markdown = None

try:
    from weasyprint import HTML
except Exception:
    HTML = None


def markdown_to_html(text: str) -> str:
    if markdown:
        return markdown.markdown(text, extensions=["extra"])  # type: ignore
    # fallback: simple paragraph wrapping
    import html as _html

    return f"<div><pre>{_html.escape(text)}</pre></div>"


def export_analysis(df, summary_text, charts_dict=None, output_dir="./output", timestamp=True, logger=None):
    """Export analysis in CSV, PDF and HTML formats.

    Parameters
    - df: pandas.DataFrame
    - summary_text: markdown string
    - charts_dict: dict(name -> plotly.figure)
    - output_dir: directory where outputs will be written
    - timestamp: whether to create a timestamped subfolder

    Returns a dict of generated file paths.
    """
    logger = logger or logging.getLogger(__name__)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S") if timestamp else ""
    out = Path(output_dir)
    if ts:
        out = out / ts
    out.mkdir(parents=True, exist_ok=True)

    # 1. CSV
    csv_path = out / "data.csv"
    try:
        df.to_csv(csv_path, index=False)
    except Exception as e:
        logger.exception("Failed to write CSV: %s", e)
        raise

    # 2. Metadata
    meta = {
        "generated": datetime.now().isoformat(),
        "records": int(len(df)),
        "columns": list(df.columns),
    }
    with open(out / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, default=str)

    # 3. HTML report
    html_summary = markdown_to_html(summary_text)
    html_parts = ["<html><head><meta charset='utf-8'><title>Analysis Report</title></head><body>", f"<h1>Analysis Report</h1>", html_summary]

    if charts_dict:
        for name, fig in charts_dict.items():
            try:
                html_parts.append(f"<h2>{name}</h2>")
                # Use plotly's to_html; allow include_plotlyjs='cdn' to avoid heavy output
                html_parts.append(fig.to_html(full_html=False, include_plotlyjs='cdn'))
            except Exception as e:
                logger.exception("Failed to embed chart %s: %s", name, e)
                html_parts.append(f"<p>Failed to render chart {name}: {e}</p>")

    html_parts.append("</body></html>")
    html_content = "\n".join(html_parts)
    html_path = out / "report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # 4. PDF (best-effort)
    pdf_path = out / "report.pdf"
    if HTML is not None:
        try:
            # convert the markdown summary (or full HTML) to PDF
            HTML(string=html_summary).write_pdf(str(pdf_path))
        except Exception as e:
            logger.exception("PDF export failed: %s", e)
    else:
        logger.warning("WeasyPrint not installed; skipping PDF generation.")

    return {
        "csv": str(csv_path),
        "html": str(html_path),
        "pdf": str(pdf_path) if pdf_path.exists() else None,
        "metadata": str(out / "metadata.json"),
        "folder": str(out),
    }
