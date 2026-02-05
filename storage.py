"""
storage.py
Manages persistence of analysis results and reports.
Structure:
  reports/
    example.com/
      data.json   <-- Raw analysis data (ComprehensiveReportData)
      report.md   <-- The human-readable prose report
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

# Import schemas to reconstruct objects
from schemas import ComprehensiveReportData

logger = logging.getLogger(__name__)

REPORTS_DIR = Path("reports")

class StorageManager:
    def __init__(self, base_dir: Path = REPORTS_DIR):
        self.base_dir = base_dir
        self.base_dir.mkdir(exist_ok=True)

    def _get_outlet_dir(self, domain: str) -> Path:
        """Sanitizes domain and returns directory path."""
        safe_domain = domain.replace("https://", "").replace("http://", "").replace("www.", "").strip("/")
        return self.base_dir / safe_domain

    def exists(self, domain: str, max_age_days: int = 30) -> bool:
        """
        Check if a valid, recent analysis exists.
        """
        outlet_dir = self._get_outlet_dir(domain)
        data_file = outlet_dir / "data.json"

        if not data_file.exists():
            return False

        # Check age
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            analysis_date = data.get("analysis_date")
            if not analysis_date:
                return False
                
            # Parse date (assuming YYYY-MM-DD format from research.py)
            date_obj = datetime.strptime(analysis_date, "%Y-%m-%d")
            if datetime.now() - date_obj > timedelta(days=max_age_days):
                logger.info(f"Cache expired for {domain}")
                return False
                
            return True
        except Exception as e:
            logger.warning(f"Error checking cache for {domain}: {e}")
            return False

    def save(self, domain: str, report_data: ComprehensiveReportData, report_text: str):
        """Saves raw data and text report."""
        outlet_dir = self._get_outlet_dir(domain)
        outlet_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save Raw Data (JSON)
        # model_dump is Pydantic v2 method (use .dict() for v1)
        json_path = outlet_dir / "data.json"
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(report_data.model_dump_json(indent=2))

        # 2. Save Text Report (Markdown)
        md_path = outlet_dir / "report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(report_text)
            
        logger.info(f"Saved report and data for {domain} to {outlet_dir}")

    def load_data(self, domain: str) -> Optional[ComprehensiveReportData]:
        """Loads raw data object from disk."""
        outlet_dir = self._get_outlet_dir(domain)
        json_path = outlet_dir / "data.json"
        
        if not json_path.exists():
            return None
            
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data_dict = json.load(f)
            return ComprehensiveReportData(**data_dict)
        except Exception as e:
            logger.error(f"Failed to load data for {domain}: {e}")
            return None

    def load_report_text(self, domain: str) -> Optional[str]:
        """Loads the text report."""
        outlet_dir = self._get_outlet_dir(domain)
        md_path = outlet_dir / "report.md"
        
        if not md_path.exists():
            return None
            
        with open(md_path, "r", encoding="utf-8") as f:
            return f.read()