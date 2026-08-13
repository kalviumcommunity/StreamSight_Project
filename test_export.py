"""
Tests for Export & Report Generation System

Tests the export manager, PDF generation, HTML generation, email delivery,
and version control modules.
"""

import pytest
import pandas as pd
from pathlib import Path
from datetime import datetime
import json
import tempfile
from unittest.mock import patch, MagicMock

from export.export_manager import ExportManager
from export.version_control import VersionControl
from export.html_generator import HTMLGenerator
from export.pdf_generator import PDFGenerator


class TestExportManager:
    """Test ExportManager functionality."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def sample_df(self):
        """Create sample DataFrame."""
        return pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'value': range(100, 110),
            'category': ['A', 'B'] * 5
        })

    def test_export_analysis_creates_directories(self, temp_dir, sample_df):
        """Test that export creates proper directory structure."""
        exporter = ExportManager(base_output_dir=temp_dir)

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test"
        )

        assert Path(result['csv']).exists()
        assert Path(result['html']).exists()
        assert Path(result['metadata']).exists()

    def test_csv_export(self, temp_dir, sample_df):
        """Test CSV export functionality."""
        exporter = ExportManager(base_output_dir=temp_dir)

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test"
        )

        # Verify CSV contains expected data
        exported_df = pd.read_csv(result['csv'])
        assert len(exported_df) == len(sample_df)
        assert list(exported_df.columns) == list(sample_df.columns)

    def test_metadata_generation(self, temp_dir, sample_df):
        """Test metadata file generation."""
        exporter = ExportManager(base_output_dir=temp_dir)

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test"
        )

        with open(result['metadata'], 'r') as f:
            metadata = json.load(f)

        assert metadata['record_count'] == len(sample_df)
        assert metadata['column_count'] == len(sample_df.columns)
        assert 'generated_timestamp' in metadata

    def test_data_dictionary(self, temp_dir, sample_df):
        """Test data dictionary inclusion."""
        exporter = ExportManager(base_output_dir=temp_dir)

        data_dict = {
            'date': 'Date field',
            'value': 'Numeric value',
            'category': 'Category'
        }

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test",
            data_dictionary=data_dict
        )

        with open(result['metadata'], 'r') as f:
            metadata = json.load(f)

        assert metadata.get('data_dictionary') == data_dict

    def test_readme_creation(self, temp_dir, sample_df):
        """Test README file creation."""
        exporter = ExportManager(base_output_dir=temp_dir)

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test"
        )

        readme_path = result['readme']
        assert Path(readme_path).exists()

        with open(readme_path, 'r') as f:
            content = f.read()

        assert 'test_report' in content
        assert 'data.csv' in content
        assert 'report.html' in content

    def test_export_with_empty_dataframe(self, temp_dir):
        """Test handling of empty DataFrame."""
        exporter = ExportManager(base_output_dir=temp_dir)
        empty_df = pd.DataFrame()

        # Should still create files even with empty data
        result = exporter.export_analysis(
            df=empty_df,
            report_name="empty_report",
            summary_text="# Empty Report"
        )

        assert Path(result['csv']).exists()

    def test_export_creates_timestamp(self, temp_dir, sample_df):
        """Test timestamp format in export."""
        exporter = ExportManager(base_output_dir=temp_dir)

        result = exporter.export_analysis(
            df=sample_df,
            report_name="test_report",
            summary_text="# Test"
        )

        # Check timestamp format: YYYY-MM-DD_HHMMSS
        assert len(result['timestamp']) == 15
        assert result['timestamp'][4] == '-'
        assert result['timestamp'][7] == '-'
        assert result['timestamp'][10] == '_'


class TestHTMLGenerator:
    """Test HTML report generation."""

    def test_html_generation(self):
        """Test basic HTML generation."""
        generator = HTMLGenerator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)

        result = generator.generate_report(
            summary_text="# Test Report",
            charts_dict={},
            report_name="Test",
            output_path=output_path,
            data_preview=None
        )

        assert result.exists()
        assert result.suffix == '.html'

        with open(output_path, 'r') as f:
            content = f.read()

        assert '<!DOCTYPE html>' in content
        assert 'Test Report' in content

        # Cleanup
        output_path.unlink()

    def test_html_with_data_preview(self):
        """Test HTML generation with data preview."""
        generator = HTMLGenerator()
        df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})

        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)

        generator.generate_report(
            summary_text="# Report",
            charts_dict={},
            report_name="Test",
            output_path=output_path,
            data_preview=df
        )

        with open(output_path, 'r') as f:
            content = f.read()

        assert 'data_preview' in content or 'table' in content.lower()

        output_path.unlink()


class TestVersionControl:
    """Test version control and history tracking."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_track_export(self, temp_dir):
        """Test export tracking."""
        vc = VersionControl(temp_dir)

        vc.track_export(
            report_name="test_report",
            timestamp="2024-01-15_143022",
            file_paths={'csv': '/path/to/data.csv', 'html': '/path/to/report.html'}
        )

        history = vc.get_report_history("test_report")
        assert history['total_exports'] == 1
        assert history['successful_exports'] == 1

    def test_get_latest_export(self, temp_dir):
        """Test retrieving latest export."""
        vc = VersionControl(temp_dir)

        vc.track_export(
            report_name="test",
            timestamp="2024-01-15_143022",
            file_paths={'csv': 'path1.csv'}
        )

        vc.track_export(
            report_name="test",
            timestamp="2024-01-16_143022",
            file_paths={'csv': 'path2.csv'}
        )

        latest = vc.get_latest_export("test")
        assert latest['timestamp'] == "2024-01-16_143022"

    def test_track_error(self, temp_dir):
        """Test error tracking."""
        vc = VersionControl(temp_dir)

        vc.track_error(
            report_name="test",
            error_message="Test error"
        )

        history = vc.get_report_history("test")
        assert history['failed_exports'] == 1
        assert history['total_exports'] == 1

    def test_generate_export_report(self, temp_dir):
        """Test export report generation."""
        vc = VersionControl(temp_dir)

        vc.track_export("report1", "2024-01-15_143022", {'csv': 'path.csv'})
        vc.track_export("report2", "2024-01-15_143023", {'csv': 'path.csv'})

        report = vc.generate_export_report()

        assert 'report1' in report
        assert 'report2' in report
        assert 'Total Exports' in report


class TestPDFGenerator:
    """Test PDF generation."""

    def test_pdf_generation_disabled_without_dependency(self):
        """Test graceful handling when WeasyPrint is unavailable."""
        generator = PDFGenerator()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            output_path = Path(f.name)

        # This should not raise an error even if WeasyPrint is unavailable
        # It will return False to indicate PDF generation was skipped
        try:
            result = generator.generate_from_markdown(
                "# Test",
                output_path
            )
            # Result is True if successful, False if WeasyPrint not available
            assert isinstance(result, bool)
        except ImportError:
            pytest.skip("WeasyPrint not installed")


class TestIntegration:
    """Integration tests for full export workflow."""

    def test_full_export_workflow(self):
        """Test complete export workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            exporter = ExportManager(base_output_dir=tmpdir)

            df = pd.DataFrame({
                'date': pd.date_range('2024-01-01', periods=5),
                'sales': [100, 150, 120, 180, 200]
            })

            result = exporter.export_analysis(
                df=df,
                report_name="sales_report",
                summary_text="# Sales Report\n\nSales are growing.",
                charts_dict={},
                metadata={'source': 'database'},
                data_dictionary={'sales': 'Daily sales'}
            )

            # Verify all files exist
            assert Path(result['csv']).exists()
            assert Path(result['html']).exists()
            assert Path(result['metadata']).exists()
            assert Path(result['readme']).exists()

            # Verify CSV content
            exported = pd.read_csv(result['csv'])
            assert len(exported) == 5

            # Verify metadata
            with open(result['metadata'], 'r') as f:
                metadata = json.load(f)
            assert metadata['record_count'] == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
