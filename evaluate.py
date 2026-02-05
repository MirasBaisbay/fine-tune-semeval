"""
Evaluation Module - Compare Media Profiler predictions against MBFC ground truth.

Uses Mean Absolute Error (MAE) with ordinal class mapping for:
- Bias Rating: 7 ordinal classes (Extreme Left=0 to Extreme Right=6)
- Factuality Rating: 6 ordinal classes (Very High=0 to Very Low=5)

Usage:
    python evaluate.py [--n 10] [--mbfc-path mbfc_data.json]
"""

import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from research import MediaProfiler
from scraper import MediaScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# Ordinal Class Mappings
# =============================================================================

# Bias Rating Scale (from user specification)
# -10 to -8.0: Extreme Left Bias  -> ordinal 0
# -7.9 to -5.0: Left Bias         -> ordinal 1
# -4.9 to -2.0: Left-Center Bias  -> ordinal 2
# -1.9 to +1.9: Least Biased      -> ordinal 3
# +2.0 to +4.9: Right-Center Bias -> ordinal 4
# +5.0 to +7.9: Right Bias        -> ordinal 5
# +8.0 to +10: Extreme Right Bias -> ordinal 6

BIAS_ORDINAL_MAP = {
    "EXTREME LEFT": 0,
    "LEFT": 1,
    "LEFT-CENTER": 2,
    "LEFT CENTER": 2,
    "LEAST BIASED": 3,
    "CENTER": 3,
    "RIGHT-CENTER": 4,
    "RIGHT CENTER": 4,
    "RIGHT": 5,
    "EXTREME RIGHT": 6,
}


def bias_score_to_ordinal(score: float) -> int:
    """
    Convert bias score (-10 to +10) to ordinal class (0-6).
    Based on User Specification:
    -10 to -8.0: Extreme Left
    -7.9 to -5.0: Left
    -4.9 to -2.0: Left-Center
    -1.9 to +1.9: Least Biased
    +2.0 to +4.9: Right-Center
    +5.0 to +7.9: Right
    +8.0 to +10: Extreme Right
    """
    if score <= -8.0:
        return 0  # Extreme Left
    elif score <= -5.0:
        return 1  # Left
    elif score <= -2.0:
        return 2  # Left-Center
    elif score <= 1.9:
        return 3  # Least Biased / Center
    elif score <= 4.9:
        return 4  # Right-Center
    elif score <= 7.9:
        return 5  # Right
    else:
        return 6  # Extreme Right


def bias_label_to_ordinal(label: str) -> int:
    """
    Convert bias label string to ordinal class.

    Args:
        label: MBFC bias label (e.g., "LEFT", "RIGHT-CENTER")

    Returns:
        Ordinal class from 0-6
    """
    normalized = label.upper().strip()
    return BIAS_ORDINAL_MAP.get(normalized, 3)  # Default to center if unknown


# Factuality Rating Scale (from user specification)
# 0 = Very High      -> ordinal 0
# 1 = High           -> ordinal 1
# 2-3 = Mostly Factual -> ordinal 2
# 3-7 = Mixed        -> ordinal 3 (using 4-7 to avoid overlap)
# 8-9 = Low          -> ordinal 4
# 10+ = Very Low     -> ordinal 5

FACTUALITY_ORDINAL_MAP = {
    "VERY HIGH": 0,
    "HIGH": 1,
    "MOSTLY FACTUAL": 2,
    "MIXED": 3,
    "LOW": 4,
    "VERY LOW": 5,
}


def factuality_score_to_ordinal(score: float) -> int:
    """
    Convert factuality score (0-10) to ordinal class (0-5).
    Based on User Specification:
    0 = Very High (0)
    1 = High (1)
    2-3 = Mostly Factual (2)
    3-7 = Mixed (3)
    8-9 = Low (4)
    10+ = Very Low (5)
    """
    if score <= 0.5:
        return 0  # Very High
    elif score <= 1.5:
        return 1  # High
    elif score <= 3.5:
        return 2  # Mostly Factual
    elif score <= 7.5:
        return 3  # Mixed
    elif score <= 9.5:
        return 4  # Low
    else:
        return 5  # Very Low
    

def factuality_label_to_ordinal(label: str) -> int:
    """
    Convert factuality label string to ordinal class.

    Args:
        label: MBFC factuality label (e.g., "HIGH", "MIXED")

    Returns:
        Ordinal class from 0-5
    """
    normalized = label.upper().strip()
    return FACTUALITY_ORDINAL_MAP.get(normalized, 3)  # Default to mixed if unknown


# =============================================================================
# Evaluation Result Data Classes
# =============================================================================

@dataclass
class SingleEvaluation:
    """Result of evaluating a single source."""
    name: str
    source_url: str

    # Ground truth (from MBFC)
    gt_bias_label: str
    gt_bias_score: float
    gt_bias_ordinal: int
    gt_factuality_label: str
    gt_factuality_score: float
    gt_factuality_ordinal: int

    # Predictions (from profiler)
    pred_bias_label: Optional[str] = None
    pred_bias_score: Optional[float] = None
    pred_bias_ordinal: Optional[int] = None
    pred_factuality_label: Optional[str] = None
    pred_factuality_score: Optional[float] = None
    pred_factuality_ordinal: Optional[int] = None

    # Errors
    bias_error: Optional[int] = None
    factuality_error: Optional[int] = None

    # Status
    success: bool = False
    error_message: Optional[str] = None
    articles_analyzed: int = 0


@dataclass
class EvaluationSummary:
    """Summary of evaluation across all sources."""
    total_sources: int
    successful_evaluations: int
    failed_evaluations: int

    # MAE scores
    bias_mae: float
    factuality_mae: float
    combined_mae: float

    # Individual results
    results: list


# =============================================================================
# Evaluation Functions
# =============================================================================

def calculate_mae(errors: list[int]) -> float:
    """Calculate Mean Absolute Error."""
    if not errors:
        return float('inf')
    return sum(abs(e) for e in errors) / len(errors)


def evaluate_single_source(
    entry: dict,
    profiler: MediaProfiler,
    max_articles: int = 20
) -> SingleEvaluation:
    """
    Evaluate profiler predictions against MBFC ground truth for a single source.

    Args:
        entry: MBFC data entry with ground truth
        profiler: MediaProfiler instance
        max_articles: Maximum articles to scrape

    Returns:
        SingleEvaluation with results
    """
    # Extract ground truth
    name = entry.get("name", "Unknown")
    source_url = entry.get("source_url", "")

    gt_bias_label = entry.get("bias_rating", "CENTER")
    gt_bias_score = entry.get("bias_score", 0.0)
    gt_factuality_label = entry.get("factual_reporting", "MIXED")
    gt_factuality_score = entry.get("factual_score", 5.0)

    # Convert ground truth to ordinal
    gt_bias_ordinal = bias_label_to_ordinal(gt_bias_label)
    gt_factuality_ordinal = factuality_label_to_ordinal(gt_factuality_label)

    evaluation = SingleEvaluation(
        name=name,
        source_url=source_url,
        gt_bias_label=gt_bias_label,
        gt_bias_score=gt_bias_score,
        gt_bias_ordinal=gt_bias_ordinal,
        gt_factuality_label=gt_factuality_label,
        gt_factuality_score=gt_factuality_score,
        gt_factuality_ordinal=gt_factuality_ordinal,
    )

    if not source_url:
        evaluation.error_message = "No source URL provided"
        return evaluation

    try:
        logger.info(f"Evaluating: {name} ({source_url})")

        # 1. Scrape articles from the source
        logger.info(f"  Scraping articles from {source_url}...")
        scraper = MediaScraper(source_url, max_articles=max_articles)
        articles = scraper.scrape_feed()

        if not articles:
            evaluation.error_message = "No articles scraped"
            return evaluation

        # Convert scraped articles to profiler format
        article_dicts = [
            {"title": a.title, "text": a.text}
            for a in articles
        ]

        logger.info(f"  Scraped {len(article_dicts)} articles")

        # 2. Run the profiler
        logger.info(f"  Running profiler...")
        report = profiler.profile(
            url=source_url,
            articles=article_dicts,
            outlet_name=name
        )

        # 3. Extract predictions
        evaluation.pred_bias_label = report.bias_label
        evaluation.pred_bias_score = report.bias_score
        evaluation.pred_bias_ordinal = bias_score_to_ordinal(report.bias_score)

        evaluation.pred_factuality_label = report.factuality_label
        evaluation.pred_factuality_score = report.factuality_score
        evaluation.pred_factuality_ordinal = factuality_score_to_ordinal(report.factuality_score)

        evaluation.articles_analyzed = report.articles_analyzed

        # 4. Calculate errors (absolute difference in ordinal classes)
        evaluation.bias_error = abs(evaluation.pred_bias_ordinal - gt_bias_ordinal)
        evaluation.factuality_error = abs(evaluation.pred_factuality_ordinal - gt_factuality_ordinal)

        evaluation.success = True

        logger.info(f"  Results for {name}:")
        logger.info(f"    Bias: GT={gt_bias_label}({gt_bias_ordinal}) Pred={report.bias_label}({evaluation.pred_bias_ordinal}) Error={evaluation.bias_error}")
        logger.info(f"    Factuality: GT={gt_factuality_label}({gt_factuality_ordinal}) Pred={report.factuality_label}({evaluation.pred_factuality_ordinal}) Error={evaluation.factuality_error}")

    except Exception as e:
        evaluation.error_message = str(e)
        logger.error(f"  Failed to evaluate {name}: {e}")

    return evaluation


def run_evaluation(
    mbfc_data: list[dict],
    n_sources: int = 10,
    max_articles: int = 20,
    model: str = "gpt-4o-mini"
) -> EvaluationSummary:
    """
    Run evaluation on first n sources from MBFC data.

    Args:
        mbfc_data: List of MBFC data entries
        n_sources: Number of sources to evaluate
        max_articles: Maximum articles to scrape per source
        model: LLM model to use

    Returns:
        EvaluationSummary with MAE scores and individual results
    """
    # Initialize profiler
    profiler = MediaProfiler(model=model)

    # Take first n sources
    sources_to_evaluate = mbfc_data[:n_sources]

    logger.info(f"Starting evaluation of {len(sources_to_evaluate)} sources")
    logger.info("=" * 70)

    results = []
    bias_errors = []
    factuality_errors = []

    for i, entry in enumerate(sources_to_evaluate, 1):
        logger.info(f"\n[{i}/{len(sources_to_evaluate)}] Processing {entry.get('name', 'Unknown')}...")

        evaluation = evaluate_single_source(entry, profiler, max_articles)
        results.append(evaluation)

        if evaluation.success:
            bias_errors.append(evaluation.bias_error)
            factuality_errors.append(evaluation.factuality_error)

    # Calculate MAE
    bias_mae = calculate_mae(bias_errors)
    factuality_mae = calculate_mae(factuality_errors)
    combined_mae = (bias_mae + factuality_mae) / 2 if bias_errors else float('inf')

    successful = sum(1 for r in results if r.success)

    summary = EvaluationSummary(
        total_sources=len(sources_to_evaluate),
        successful_evaluations=successful,
        failed_evaluations=len(sources_to_evaluate) - successful,
        bias_mae=bias_mae,
        factuality_mae=factuality_mae,
        combined_mae=combined_mae,
        results=results
    )

    return summary


def print_evaluation_report(summary: EvaluationSummary):
    """Print a formatted evaluation report."""
    print("\n" + "=" * 70)
    print("EVALUATION REPORT")
    print("=" * 70)

    print(f"\nSources Evaluated: {summary.total_sources}")
    print(f"Successful: {summary.successful_evaluations}")
    print(f"Failed: {summary.failed_evaluations}")

    print("\n" + "-" * 40)
    print("MEAN ABSOLUTE ERROR (MAE)")
    print("-" * 40)
    print(f"  Bias MAE:       {summary.bias_mae:.3f}")
    print(f"  Factuality MAE: {summary.factuality_mae:.3f}")
    print(f"  Combined MAE:   {summary.combined_mae:.3f}")

    print("\n" + "-" * 40)
    print("ORDINAL CLASS INTERPRETATION")
    print("-" * 40)
    print("  Bias: 0=Extreme Left, 1=Left, 2=Left-Center, 3=Center, 4=Right-Center, 5=Right, 6=Extreme Right")
    print("  Factuality: 0=Very High, 1=High, 2=Mostly Factual, 3=Mixed, 4=Low, 5=Very Low")
    print("  MAE=0 means perfect prediction, MAE=1 means off by one category on average")

    print("\n" + "-" * 40)
    print("INDIVIDUAL RESULTS")
    print("-" * 40)

    for r in summary.results:
        status = "OK" if r.success else "FAIL"
        print(f"\n[{status}] {r.name}")
        print(f"  URL: {r.source_url}")

        if r.success:
            print(f"  Articles Analyzed: {r.articles_analyzed}")
            print(f"  Bias:       GT={r.gt_bias_label}({r.gt_bias_ordinal}) -> Pred={r.pred_bias_label}({r.pred_bias_ordinal}) | Error={r.bias_error}")
            print(f"  Factuality: GT={r.gt_factuality_label}({r.gt_factuality_ordinal}) -> Pred={r.pred_factuality_label}({r.pred_factuality_ordinal}) | Error={r.factuality_error}")
        else:
            print(f"  Error: {r.error_message}")

    print("\n" + "=" * 70)


def save_results_json(summary: EvaluationSummary, output_path: str):
    """Save evaluation results to JSON file."""
    output = {
        "summary": {
            "total_sources": summary.total_sources,
            "successful_evaluations": summary.successful_evaluations,
            "failed_evaluations": summary.failed_evaluations,
            "bias_mae": summary.bias_mae,
            "factuality_mae": summary.factuality_mae,
            "combined_mae": summary.combined_mae,
        },
        "results": [
            {
                "name": r.name,
                "source_url": r.source_url,
                "success": r.success,
                "error_message": r.error_message,
                "articles_analyzed": r.articles_analyzed,
                "ground_truth": {
                    "bias_label": r.gt_bias_label,
                    "bias_score": r.gt_bias_score,
                    "bias_ordinal": r.gt_bias_ordinal,
                    "factuality_label": r.gt_factuality_label,
                    "factuality_score": r.gt_factuality_score,
                    "factuality_ordinal": r.gt_factuality_ordinal,
                },
                "predictions": {
                    "bias_label": r.pred_bias_label,
                    "bias_score": r.pred_bias_score,
                    "bias_ordinal": r.pred_bias_ordinal,
                    "factuality_label": r.pred_factuality_label,
                    "factuality_score": r.pred_factuality_score,
                    "factuality_ordinal": r.pred_factuality_ordinal,
                } if r.success else None,
                "errors": {
                    "bias_error": r.bias_error,
                    "factuality_error": r.factuality_error,
                } if r.success else None,
            }
            for r in summary.results
        ]
    }

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    logger.info(f"Results saved to {output_path}")


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Media Profiler against MBFC ground truth using ordinal MAE"
    )
    parser.add_argument(
        "--mbfc-path",
        type=str,
        default="mbfc_data.json",
        help="Path to MBFC data JSON file (default: mbfc_data.json)"
    )
    parser.add_argument(
        "-n", "--num-sources",
        type=int,
        default=10,
        help="Number of sources to evaluate (default: 10)"
    )
    parser.add_argument(
        "--max-articles",
        type=int,
        default=20,
        help="Maximum articles to scrape per source (default: 20)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o-mini",
        help="LLM model to use (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_results.json",
        help="Output path for JSON results (default: evaluation_results.json)"
    )

    args = parser.parse_args()

    # Load MBFC data
    mbfc_path = Path(args.mbfc_path)
    if not mbfc_path.exists():
        logger.error(f"MBFC data file not found: {mbfc_path}")
        logger.info("Please ensure mbfc_data.json exists in the project directory")
        return

    logger.info(f"Loading MBFC data from {mbfc_path}")
    with open(mbfc_path) as f:
        mbfc_data = json.load(f)

    logger.info(f"Loaded {len(mbfc_data)} sources from MBFC data")

    # Run evaluation
    summary = run_evaluation(
        mbfc_data=mbfc_data,
        n_sources=args.num_sources,
        max_articles=args.max_articles,
        model=args.model
    )

    # Print report
    print_evaluation_report(summary)

    # Save JSON results
    save_results_json(summary, args.output)


if __name__ == "__main__":
    main()
