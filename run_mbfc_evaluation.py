import json
import time
import pandas as pd
from typing import Dict, Any, List
from sklearn.metrics import accuracy_score, classification_report
from dataclasses import asdict

# Import your pipeline components
# Ensure these match your actual file names (scraper.py and research.py)
try:
    from scraper import MediaScraper
    from research import MediaProfiler
except ImportError:
    print("Warning: 'scraper' or 'research' modules not found. Ensure they exist in the directory.")
    # Mock classes for syntax checking if files are missing
    class MediaScraper:
        def __init__(self, base_url=None): pass
        def scrape_feed(self): return []
    class MediaProfiler:
        def profile(self, url, articles): return None

# Configuration
INPUT_FILE = "mbfc_data_test.json"
OUTPUT_FILE = "evaluation_results_full.json"
REPORT_FILE = "evaluation_summary.md"

class PipelineEvaluator:
    def __init__(self):
        # MediaScraper requires a URL at init, so we instantiate it inside the loop later
        self.profiler = MediaProfiler()
        self.results = []
        
    def normalize_bias_label(self, label: str) -> str:
        """Maps MBFC labels to System labels for comparison."""
        if not label: return "Unknown"
        label = label.upper().replace("-", " ").strip()
        
        # Mapping rules based on your README vs MBFC Data
        mapping = {
            "LEAST BIASED": "Center",      # MBFC 'Least Biased' -> System 'Center'
            "LEFT CENTER": "Left-Center",
            "RIGHT CENTER": "Right-Center",
            "LEFT": "Left",
            "RIGHT": "Right",
            "EXTREME LEFT": "Left",
            "EXTREME RIGHT": "Right",
            "PSEUDOSCIENCE": "Pseudoscience"
        }
        return mapping.get(label, label)

    def normalize_factuality(self, label: str) -> str:
        """Maps MBFC Factuality to System Factuality."""
        if not label: return "Unknown"
        label = label.upper().strip()
        
        # System labels: Very High, High, Mixed, Low, Very Low
        mapping = {
            "VERY HIGH": "Very High",
            "HIGH": "High",
            "MOSTLY FACTUAL": "High",  # Map 'Mostly Factual' to 'High'
            "MIXED": "Mixed",
            "LOW": "Low",
            "VERY LOW": "Very Low"
        }
        return mapping.get(label, "Mixed")

    def run(self):
        # 1. Load Ground Truth
        try:
            with open(INPUT_FILE, "r") as f:
                ground_truth_data = json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {INPUT_FILE} not found. Please create it first.")
            return

        print(f"Loaded {len(ground_truth_data)} entries from {INPUT_FILE}")

        # 2. Iterate and Process
        for entry in ground_truth_data:
            url = entry.get("source_url")
            name = entry.get("name")
            
            # Skip invalid URLs often found in raw MBFC data
            if not url or "addtoany" in url: 
                continue

            print(f"\n--- Processing: {name} ({url}) ---")

            try:
                # A. Scrape
                print("1. Scraping articles...")
                
                # Initialize scraper with the current URL
                scraper = MediaScraper(url)
                
                # Corrected: Call scrape_feed() instead of scrape()
                # Returns List[Article] dataclasses
                scraped_objects = scraper.scrape_feed()
                
                # Corrected: Convert dataclasses to list of dictionaries for the profiler
                # The profiler expects list[dict] with 'title' and 'text' keys
                articles = [asdict(obj) for obj in scraped_objects]
                
                if not articles:
                    print(f"❌ No articles found for {name}. Skipping analysis.")
                    self.results.append({
                        "name": name,
                        "url": url,
                        "status": "FAILED_SCRAPE",
                        "ground_truth": entry
                    })
                    continue

                # B. Analyze (Profile)
                print(f"2. Analyzing {len(articles)} articles...")
                report = self.profiler.profile(url, articles)

                # C. Compare
                gt_bias = self.normalize_bias_label(entry.get("bias_rating"))
                
                # System Bias Label Logic
                sys_bias = report.editorial_bias_result.mbfc_label
                
                # Special Logic: If Pseudoscience score is high, override political label
                # to match MBFC's "PSEUDOSCIENCE" category behavior
                if hasattr(report, 'pseudoscience_result') and report.pseudoscience_result:
                    if report.pseudoscience_result.score >= 6.0: 
                        sys_bias = "Pseudoscience"

                # Normalize System output
                if sys_bias == "Least Biased": 
                    sys_bias = "Center"

                gt_fact = self.normalize_factuality(entry.get("factual_reporting"))
                sys_fact = report.factuality_label

                match_bias = (gt_bias.lower() == sys_bias.lower())
                match_fact = (gt_fact.lower() == sys_fact.lower())

                print(f"   Bias: GT=[{gt_bias}] vs System=[{sys_bias}] -> {'✅' if match_bias else '❌'}")
                print(f"   Fact: GT=[{gt_fact}] vs System=[{sys_fact}] -> {'✅' if match_fact else '❌'}")

                # D. Store Result
                self.results.append({
                    "name": name,
                    "url": url,
                    "status": "SUCCESS",
                    "ground_truth": {
                        "bias": gt_bias,
                        "factuality": gt_fact,
                        "credibility": entry.get("credibility_rating")
                    },
                    "system_output": {
                        "bias": sys_bias,
                        "bias_score": report.bias_score,
                        "factuality": sys_fact,
                        "factuality_score": report.factuality_score,
                        "credibility": report.credibility_label
                    },
                    "matches": {
                        "bias": match_bias,
                        "factuality": match_fact
                    }
                })
                
                # Respect rate limits
                time.sleep(2)

            except Exception as e:
                print(f"❌ Error processing {name}: {str(e)}")
                self.results.append({
                    "name": name,
                    "url": url,
                    "status": "ERROR",
                    "error": str(e)
                })

        # 3. Save Results
        with open(OUTPUT_FILE, "w") as f:
            json.dump(self.results, f, indent=2)
        
        self.generate_report()

    def generate_report(self):
        print("\n--- Generating Metrics ---")
        
        successful = [r for r in self.results if r["status"] == "SUCCESS"]
        if not successful:
            print("No successful analyses to evaluate.")
            return

        y_true_bias = [r["ground_truth"]["bias"] for r in successful]
        y_pred_bias = [r["system_output"]["bias"] for r in successful]
        
        y_true_fact = [r["ground_truth"]["factuality"] for r in successful]
        y_pred_fact = [r["system_output"]["factuality"] for r in successful]

        # Calculate Accuracy
        acc_bias = accuracy_score(y_true_bias, y_pred_bias)
        acc_fact = accuracy_score(y_true_fact, y_pred_fact)

        # Construct Summary String
        summary = f"""# Evaluation Report

**Total Processed:** {len(self.results)}
**Successful:** {len(successful)}
**Failed:** {len(self.results) - len(successful)}

## Performance Metrics

| Metric | Accuracy |
|--------|----------|
| **Bias Label** | {acc_bias:.2%} |
| **Factuality Label** | {acc_fact:.2%} |

## Detailed Bias Report
```text
{classification_report(y_true_bias, y_pred_bias, zero_division=0)}
```

## Detailed Factuality Report
```text
{classification_report(y_true_fact, y_pred_fact, zero_division=0)}
```

## Mismatches
"""
        # Loop through successful results to find mismatches
        for r in successful:
            if not r["matches"]["bias"] or not r["matches"]["factuality"]:
                summary += f"- **{r['name']}**\n"
                if not r["matches"]["bias"]:
                    summary += f"  - Bias: GT `{r['ground_truth']['bias']}` vs Sys `{r['system_output']['bias']}`\n"
                if not r["matches"]["factuality"]:
                    summary += f"  - Fact: GT `{r['ground_truth']['factuality']}` vs Sys `{r['system_output']['factuality']}`\n"


        # Write summary to file
        with open(REPORT_FILE, "w") as f:
            f.write(summary)
        
        print(f"Report saved to {REPORT_FILE}")
        print(f"Full JSON results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    evaluator = PipelineEvaluator()
    evaluator.run()