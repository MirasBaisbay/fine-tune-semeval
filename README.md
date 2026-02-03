# Media Profiler

A comprehensive media source analysis system that evaluates news outlets for **political bias**, **factual reliability**, and **overall credibility** using the [Media Bias/Fact Check (MBFC)](https://mediabiasfactcheck.com/methodology/) methodology.

## Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Methodology](#methodology)
  - [Bias Scoring](#bias-scoring)
  - [Factuality Scoring](#factuality-scoring)
  - [Credibility Calculation](#credibility-calculation)
- [Core Modules](#core-modules)
- [Ideology Detection System](#ideology-detection-system)
- [Propaganda Detection](#propaganda-detection)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [References](#references)

---

## Overview

Media Profiler automates the evaluation of news sources by:

1. **Scraping** articles from target news websites
2. **Analyzing** content across 8 weighted dimensions (4 bias + 4 factuality)
3. **Detecting** propaganda techniques using fine-tuned DeBERTa models
4. **Evaluating** ideology through structured decision-tree questioning
5. **Calculating** composite scores following MBFC methodology
6. **Generating** detailed credibility reports

### Key Features

- **MBFC-Compliant Scoring** - Implements exact weighting system used by Media Bias/Fact Check
- **Two-Stage Propaganda Detection** - DeBERTa-v3-Large for span identification + technique classification
- **Decision-Tree Ideology Analysis** - Recursive question-based evaluation with academic backing
- **Editorial Bias Detection** - Clickbait patterns, loaded language, emotional manipulation
- **Human-in-the-Loop Verification** - Optional manual review of AI findings
- **Country Freedom Adjustment** - RSF/Freedom House press freedom ratings

---

## System Architecture

### Complete Analysis Pipeline

```
                         MEDIA PROFILER - COMPLETE PIPELINE
================================================================================

                                   INPUT
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. SCRAPE NODE (scraper.py)                                                │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  MediaScraper                                                   │     │
│     │  ├── Fetch homepage + sitemap                                   │     │
│     │  ├── Collect up to 20 articles                                  │     │
│     │  ├── Separate News vs Opinion articles                          │     │
│     │  │   ├── URL patterns (/opinion/, /editorial/)                  │     │
│     │  │   ├── Schema.org metadata                                    │     │
│     │  │   └── Title patterns ("Opinion:", "Editorial:")              │     │
│     │  └── Extract site metadata                                      │     │
│     │       ├── About page (ownership, funding)                       │     │
│     │       ├── Author information                                    │     │
│     │       └── Location disclosure                                   │     │
│     └─────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. ANALYZE NODE (analyzers.py)                                             │
│                                                                             │
│     ┌───────────────────────────┐   ┌───────────────────────────┐           │
│     │    BIAS ANALYZERS (4)     │   │  FACTUALITY ANALYZERS (4) │           │
│     ├───────────────────────────┤   ├───────────────────────────┤           │
│     │ EconomicAnalyzer (35%)    │   │ FactCheckSearcher (40%)   │           │
│     │ SocialAnalyzer (35%)      │   │ SourcingAnalyzer (25%)    │           │
│     │ NewsReporting (15%)       │   │ TransparencyAnalyzer (25%)│           │
│     │ EditorialBias (15%)       │   │ PropagandaAnalyzer (10%)  │           │
│     └───────────────────────────┘   └───────────────────────────┘           │
│                                                                             │
│     ┌───────────────────────────────────────────────────────────────────┐   │
│     │  SUPPORTING ANALYZERS                                             │   │
│     │  ├── MediaTypeAnalyzer → TV Station / Newspaper / Website         │   │
│     │  ├── CountryFreedomAnalyzer → 2025.csv → Freedom Rating           │   │
│     │  └── TrafficLongevityAnalyzer → High/Medium/Minimal + Age         │   │
│     └───────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. REPORT NODE (profiler.py)                                               │
│     ┌─────────────────────────────────────────────────────────────────┐     │
│     │  ScoringCalculator                                              │     │
│     │  ├── calculate_bias() → Weighted average → BIAS LABEL           │     │
│     │  ├── calculate_factuality() → Weighted average → FACT LABEL     │     │
│     │  └── calculate_credibility() → Points system → CREDIBILITY      │     │
│     └─────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
                                  OUTPUT
```

### Scoring Components

```
+-----------------------------------------------------------------------------+
|           BIAS SCORING (-10 to +10)    |    FACTUALITY SCORING (0-10)       |
|----------------------------------------|-------------------------------------|
|                                        |                                     |
|  EconomicAnalyzer           (35%)      |  FactCheckSearcher        (40%)    |
|  -10 Communism -> +10 Laissez-Faire    |  IFCN-approved fact-checker search |
|                                        |                                     |
|  SocialAnalyzer             (35%)      |  SourcingAnalyzer         (25%)    |
|  -10 Progressive -> +10 Traditional    |  Hyperlink/citation quality        |
|                                        |                                     |
|  NewsReportingAnalyzer      (15%)      |  TransparencyAnalyzer     (25%)    |
|  Balance in straight news              |  Ownership/funding disclosure      |
|                                        |                                     |
|  EditorialBiasAnalyzer      (15%)      |  PropagandaAnalyzer       (10%)    |
|  Opinion/editorial lean                |  DeBERTa SI+TC pipeline            |
|                                        |                                     |
+-----------------------------------------------------------------------------+
|                                                                             |
|                           CREDIBILITY SCORE (0-10)                          |
|  = Factuality Points + Bias Points + Traffic Bonus + Freedom Penalty        |
|                                                                             |
+-----------------------------------------------------------------------------+
```

---

## Methodology

### Bias Scoring

Scale: **-10 (Extreme Left) to +10 (Extreme Right)**

| Component | Weight | Range | Description |
|-----------|--------|-------|-------------|
| **Economic System** | 35% | -10 to +10 | Communism to Radical Laissez-Faire |
| **Social Values** | 35% | -10 to +10 | Strong Progressive to Strong Traditional |
| **News Reporting** | 15% | -10 to +10 | Balance in straight news coverage |
| **Editorial Bias** | 15% | -10 to +10 | Bias in opinion/editorial pieces |

**Bias Labels:**
| Score Range | Label |
|-------------|-------|
| -10 to -8.0 | Extreme Left |
| -7.9 to -5.0 | Left |
| -4.9 to -2.0 | Left-Center |
| -1.9 to +1.9 | Least Biased |
| +2.0 to +4.9 | Right-Center |
| +5.0 to +7.9 | Right |
| +8.0 to +10 | Extreme Right |

### Factuality Scoring

Scale: **0 (Best) to 10 (Worst)**

| Component | Weight | Description |
|-----------|--------|-------------|
| **Failed Fact Checks** | 40% | Count from IFCN-approved fact-checkers |
| **Sourcing Quality** | 25% | Hyperlinks, citations, credible references |
| **Transparency** | 25% | Ownership, funding, authorship disclosure |
| **Propaganda** | 10% | Detected propaganda techniques |

**Factuality Labels:**
| Score Range | Label |
|-------------|-------|
| 0.0 - 0.4 | Very High |
| 0.5 - 1.9 | High |
| 2.0 - 4.4 | Mostly Factual |
| 4.5 - 6.4 | Mixed |
| 6.5 - 8.4 | Low |
| 8.5 - 10.0 | Very Low |

### Credibility Calculation

```
Credibility = Factuality Points + Bias Points + Traffic Bonus + Freedom Penalty

Where:
  Factuality Points: Very High=4, High=3, Mostly Factual=2, Mixed=1, Low/Very Low=0
  Bias Points:       Least Biased=3, Center=2, Left/Right=1, Extreme=0
  Traffic Bonus:     High=2, Medium=1, Minimal=0, +1 if >10 years old
  Freedom Penalty:   Limited Freedom=-1, Total Oppression=-2
```

**Credibility Levels:**
- **6-10**: High Credibility
- **3-5**: Medium Credibility
- **0-2**: Low Credibility

---

## Core Modules

### profiler.py - Orchestration Workflow

LangGraph-based workflow orchestrator with human-in-the-loop capabilities.

```bash
python profiler.py <url> <country> [--model {llm,local}] [--no-review]
```

**Pipeline Nodes:**
1. `scrape_node()` - Collects articles and metadata
2. `analyze_node()` - Runs all 8 analyzers
3. `report_node()` - Generates MBFC-compliant report

### analyzers.py - Analysis Engine

Core module implementing all MBFC-compliant scoring components:

**Bias Analyzers:**
- `EconomicAnalyzer` - Economic ideology (-10 to +10)
- `SocialAnalyzer` - Social values stance (-10 to +10)
- `NewsReportingBalanceAnalyzer` - News balance evaluation
- `EditorialBiasAnalyzer` - Editorial/opinion bias
- `IdeologyDecisionTreeAnalyzer` - Recursive decision-tree ideology detection

**Factuality Analyzers:**
- `FactCheckSearcher` - IFCN fact-checker search
- `SourcingAnalyzer` - Source quality evaluation
- `TransparencyAnalyzer` - Disclosure assessment
- `PropagandaAnalyzer` - Propaganda detection (DeBERTa/LLM)

**Supporting Analyzers:**
- `CountryFreedomAnalyzer` - Freedom House/RSF ratings
- `TrafficLongevityAnalyzer` - Traffic and age estimation
- `MediaTypeAnalyzer` - Media type classification

### scraper.py - Web Scraping Engine

Brute-force article collection with:
- Browser-like headers to avoid blocking
- Rate limiting (0.5-1.5s delays)
- Threaded parallel scraping (5 workers)
- Opinion article detection (URL, title, meta tags, schema.org)
- Metadata extraction (about page, ownership, funding, authors)

### editorial_bias_detection.py - Editorial Analysis

Specialized module for detecting:
- **Clickbait patterns** (12+ patterns from academic research)
- **Loaded language** (left/right terms, intensifiers, emotional words)
- **Emotional manipulation** (sentiment extremity, framing bias)

Based on research by:
- Recasens et al. (2013) - Linguistic Models for Bias Detection
- Chakraborty et al. (2016) - Clickbait Detection
- QCRI - Emotional Language Analysis

---

## Analyzer Flow Diagrams

### Editorial Bias Analyzer (15% of Bias Score)

```
                    EDITORIAL BIAS ANALYZER
+------------------------------------------------------------------+
│  INPUT: Opinion/Editorial Articles                                │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  1. CLICKBAIT DETECTION (Rule-Based)                              │
│     ├── 14 regex patterns from Chakraborty et al.                 │
│     │   ├── 5W1H questions ("What happened when...")              │
│     │   ├── Forward references ("This will shock you")            │
│     │   ├── Listicles ("10 Things You Need to Know")              │
│     │   └── Emotional triggers, superlatives, urgency             │
│     └── Severity scoring (0.0 - 1.0)                              │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  2. LOADED LANGUAGE DETECTION (Lexicon-Based)                     │
│     ├── Left-loaded terms (27): "far-right", "bigot", "regime"    │
│     ├── Right-loaded terms (24): "woke", "radical left", "marxist"│
│     ├── Subjective intensifiers (19): "extremely", "utterly"      │
│     ├── Emotional words (26 negative + 16 positive)               │
│     └── Doubt markers (8): "so-called", "self-proclaimed"         │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  3. LLM DIRECTION DETECTION                                       │
│     └── If rule-based inconclusive → LLM determines left/right    │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  4. SCORE CALCULATION                                             │
│     intensity = (loaded_language * 0.4) + (manipulation * 0.4)    │
│                 + (clickbait * 0.2)                               │
│     score = intensity * direction * confidence                    │
│     → Clamp to [-10, +10]                                         │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  OUTPUT: EditorialBiasAnalysis                                    │
│    ├── overall_score: -10 to +10                                  │
│    ├── overall_label: "Moderate Left Editorial Bias"              │
│    ├── clickbait_score: 0-10                                      │
│    ├── loaded_language_score: 0-10                                │
│    └── direction: "left" / "right" / "neutral"                    │
+------------------------------------------------------------------+
```

### News Reporting Balance Analyzer (15% of Bias Score)

```
                  NEWS REPORTING BALANCE ANALYZER
+------------------------------------------------------------------+
│  INPUT: Straight News Articles (non-opinion)                      │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  1. FILTER & SELECT                                               │
│     └── Up to 15 news articles (exclude opinion/editorial)        │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  2. PER-ARTICLE LLM ANALYSIS                                      │
│     For each article → JSON:                                      │
│     {                                                             │
│       "topic_lean": "left" | "right" | "neutral",                 │
│       "sourcing": "multi-sided" | "one-sided" | "no-sources",     │
│       "framing": "neutral" | "left-leaning" | "right-leaning",    │
│       "evidence": "Brief observation"                             │
│     }                                                             │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  3. MATHEMATICAL SCORING                                          │
│                                                                   │
│  A. Story Selection (40%):                                        │
│     ratio = (right_topics - left_topics) / (total + 1)            │
│     weight = political_topics / total                             │
│     selection_score = ratio * 10 * weight                         │
│                                                                   │
│  B. Framing (30%):                                                │
│     ratio = (right_framing - left_framing) / (total + 1)          │
│     framing_score = ratio * 10                                    │
│                                                                   │
│  C. Sourcing Modifier:                                            │
│     diversity = multi_sided / total                               │
│     modifier = 1.5 (if <30%) | 1.0 (30-70%) | 0.6 (if >70%)       │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  4. FINAL CALCULATION                                             │
│     base = (selection * 0.4) + (framing * 0.6)                    │
│     final = base * sourcing_modifier                              │
│     → Clamp to [-10, +10]                                         │
+------------------------------------------------------------------+
                              │
                              ▼
+------------------------------------------------------------------+
│  OUTPUT: NewsReportingAnalysis                                    │
│    ├── overall_score: -10 to +10                                  │
│    ├── overall_label: "Mild Left Reporting"                       │
│    ├── story_selection_score, framing_score                       │
│    ├── sourcing_diversity, sourcing_modifier                      │
│    └── article_analyses: per-article breakdown                    │
+------------------------------------------------------------------+
```

### Propaganda Detection (10% of Factuality Score)

```
                      PROPAGANDA DETECTION
+------------------------------------------------------------------+
│  INPUT: Article text (up to 5 articles, 1500 chars each)          │
+------------------------------------------------------------------+
                              │
            ┌─────────────────┴─────────────────┐
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│  LOCAL MODE (DeBERTa) │           │  LLM MODE (Fallback)  │
├───────────────────────┤           ├───────────────────────┤
│                       │           │                       │
│  STAGE 1: SI Model    │           │  GPT-4o-mini prompt   │
│  (Span Identification)│           │  ├── 14 techniques    │
│  Token Classification │           │  └── JSON output      │
│  → BIO tagging        │           │                       │
│  → Find WHERE         │           └───────────────────────┘
│                       │
│  STAGE 2: TC Model    │
│  (Technique Class.)   │
│  Sequence Class.      │
│  → 14 categories      │
│  → Identify WHICH     │
│                       │
└───────────────────────┘
            │                                   │
            └─────────────────┬─────────────────┘
                              ▼
+------------------------------------------------------------------+
│  OUTPUT: PropagandaAnalysis                                       │
│    ├── score: 0-10 (instances * 1.5, capped)                      │
│    └── instances: List[PropagandaInstance]                        │
│          ├── text_snippet                                         │
│          ├── technique (14 categories)                            │
│          ├── confidence                                           │
│          └── context                                              │
+------------------------------------------------------------------+
```

---

### parser.py - MBFC Website Parser

Specialized parser for scraping Media Bias/Fact Check website to collect source URLs.

---

## Ideology Detection System

The `IdeologyDecisionTreeAnalyzer` implements a recursive decision-tree approach to ideology detection using the `ideology_question_bank.json`.

### Execution Flow

```
                    IDEOLOGY DECISION TREE
+------------------------------------------------------------------+
|  1. TOPIC FILTER                                                  |
|     Run preliminary_check for each topic                          |
|     If NO -> Score as None (exclude from average)                 |
|     If YES -> Proceed to Step 2                                   |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|  2. STANCE DETECTION (The Fork)                                   |
|     Ask LLM: "Does this article lean LEFT or RIGHT?"              |
|     If Left -> Execute left_leaning branch starting from L1       |
|     If Right -> Execute right_leaning branch starting from R4     |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|  3. THE "STOP" CONDITION                                          |
|                                                                   |
|  LEFT BRANCH (check extremes first!):                             |
|    Ask L1 (Extreme -10) -> If Yes: Score -10, STOP                |
|    If No -> Ask L2 (-7.5) -> If Yes: Score -7.5, STOP             |
|    If No -> Ask L3 (-5) -> If Yes: Score -5, STOP                 |
|    If No -> Ask L4 (-2.5) -> If Yes: Score -2.5, STOP             |
|    If all No -> Check Centrism                                    |
|                                                                   |
|  RIGHT BRANCH (check extremes first!):                            |
|    Ask R4 (Extreme +10) -> If Yes: Score +10, STOP                |
|    If No -> Ask R3 (+7.5) -> If Yes: Score +7.5, STOP             |
|    If No -> Ask R2 (+5) -> If Yes: Score +5, STOP                 |
|    If No -> Ask R1 (+2.5) -> If Yes: Score +2.5, STOP             |
|    If all No -> Check Centrism                                    |
+------------------------------------------------------------------+
```

### Why Check Extremes First

If you ask the Moderate question first (e.g., "Do you support unions?"), a Communist would say "Yes." You would incorrectly score them as -5 instead of -10.

**Always check extremes first to avoid misclassification.**

### Question Bank Structure

The `ideology_question_bank.json` contains:

**Economic System Dimension (35% weight):**
- Government Ownership and Industry Control
- Taxation Policy
- Labor Rights and Unions
- Corporate Regulation
- Trade and Globalization
- Social Welfare Programs
- Financial Sector Regulation

**Social Values Dimension (35% weight):**
- LGBTQ+ Rights
- Abortion and Reproductive Rights
- Immigration (Social perspective)
- Climate Change and Environment
- Racial Justice and Civil Rights
- Gun Rights
- Religious Liberty

Each topic includes:
- `preliminary_check` - Relevance filter
- `left_leaning` / `progressive_leaning` - Questions ordered L1 (extreme) to L4 (moderate)
- `right_leaning` / `conservative_leaning` - Questions ordered R4 (extreme) to R1 (moderate)
- `centrism` - Balanced position check
- Academic references for each question

---

## Propaganda Detection

### Two-Stage DeBERTa Pipeline

```
INPUT: "The radical left wants to destroy our great nation..."

+------------------------------------------------------------------+
|  STAGE 1: SPAN IDENTIFICATION (SI)                                |
|  Model: DeBERTa-v3-Large (Token Classification, BIO tagging)      |
|  Task: Find WHERE propaganda exists                               |
|                                                                   |
|  Input:  ["The", "radical", "left", "wants", "to", ...]          |
|  Output: [ O,    B-PROP,   I-PROP,  O,      O,  ...]              |
|                  ^^^^^^^^^^^^^^                                   |
|                  Detected Span                                    |
+------------------------------------------------------------------+
                              |
                              v
+------------------------------------------------------------------+
|  STAGE 2: TECHNIQUE CLASSIFICATION (TC)                           |
|  Model: DeBERTa-v3-Large (Sequence Classification, 14 classes)    |
|  Task: Identify WHICH technique is used                           |
|                                                                   |
|  Input:  "[Context] [SEP] radical left"                           |
|  Output: "Name_Calling,Labeling" (confidence: 0.87)               |
+------------------------------------------------------------------+
```

### Propaganda Techniques (14 Classes)

| # | Technique | Description |
|---|-----------|-------------|
| 1 | Appeal_to_Authority | Citing authority figures to support claims |
| 2 | Appeal_to_fear-prejudice | Using fear or prejudice to influence |
| 3 | Bandwagon,Reductio_ad_Hitlerum | "Everyone does it" or Nazi comparisons |
| 4 | Black-and-White_Fallacy | Presenting only two choices |
| 5 | Causal_Oversimplification | Oversimplifying cause-effect |
| 6 | Doubt | Questioning credibility without evidence |
| 7 | Exaggeration,Minimisation | Overstating or understating facts |
| 8 | Flag-Waving | Appealing to patriotism/nationalism |
| 9 | Loaded_Language | Using emotionally charged words |
| 10 | Name_Calling,Labeling | Using derogatory labels |
| 11 | Repetition | Repeating messages for emphasis |
| 12 | Slogans | Using catchy phrases |
| 13 | Thought-terminating_Cliches | Phrases discouraging critical thinking |
| 14 | Whataboutism,Straw_Men,Red_Herring | Deflection tactics |

### Training Configuration

```python
Model: microsoft/deberta-v3-large (304M parameters)

SI Model (Span Identification):
  max_length = 512
  learning_rate = 1e-5
  batch_size = 4 (effective 32 with accumulation)
  epochs = 15

TC Model (Technique Classification):
  max_length = 384
  learning_rate = 1.5e-5
  batch_size = 8 (effective 64 with accumulation)
  epochs = 10

Features:
  - Focal loss for class imbalance
  - Early stopping (patience=4)
  - SemEval 2020 Task 11 dataset
```

---

## Installation

### Requirements

- Python 3.8+
- PyTorch with CUDA (recommended for training)
- 16GB+ RAM for inference
- 24GB+ GPU VRAM for training

### Setup

```bash
# Clone repository
git clone https://github.com/MirasBaisbay/media-profiling.git
cd media-profiling

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install torch transformers datasets langgraph beautifulsoup4 \
            requests scikit-learn duckduckgo-search openai langchain-openai

# Set API key (for LLM-based analyzers)
export OPENAI_API_KEY="your-api-key"
```

### Train Models (Optional)

```bash
# Ensure datasets/ folder contains SemEval 2020 Task 11 data
python trainPipeline.py
```

---

## Usage

### Command Line

```bash
# Analyze with local DeBERTa models
python profiler.py https://example-news.com US --model local

# Analyze with LLM fallback
python profiler.py https://example-news.com GB --model llm

# Skip human review
python profiler.py https://example-news.com US --model local --no-review
```

### Programmatic

```python
from profiler import app

result = app.invoke({
    "target_url": "https://example-news.com",
    "country_code": "US",
    "use_local_model": True
})

print(result["final_report"])
```

### Sample Output

```
Detailed Report for bbc.com
Bias Rating: LEFT-CENTER (-2.3)
Factual Reporting: HIGH (1.1)
Country: United Kingdom
MBFC's Country Freedom Rating: MOSTLY FREE
Media Type: TV Station
Traffic/Popularity: High Traffic
MBFC Credibility Rating: HIGH CREDIBILITY
```

---

## Example: Analyzing BBC.com

This walkthrough demonstrates the complete analysis pipeline for a real media outlet.

### Step 1: Parse Articles

```bash
$ python profiler.py https://www.bbc.com GB --model local

[INFO] Scraping https://www.bbc.com...
[INFO] Found sitemap: /sitemap.xml
[INFO] Collecting articles from news sections...
[INFO] Scraped 20 articles: 16 news, 4 opinion/editorial
```

**Articles collected:**
```
NEWS:
  1. "UK inflation falls to 2.1% in latest figures"
  2. "Election polls show tight race in key constituencies"
  3. "Climate summit reaches new agreement on emissions"
  ... (13 more news articles)

OPINION:
  1. "Analysis: What the economic data means for households"
  2. "Comment: The future of British foreign policy"
  ... (2 more opinion pieces)
```

### Step 2: Select Articles for Analysis

```
[INFO] Separating articles by type for MBFC methodology...
[INFO] News articles (16) → NewsReportingBalanceAnalyzer, EconomicAnalyzer, SocialAnalyzer
[INFO] Opinion articles (4) → EditorialBiasAnalyzer
```

### Step 3: Run Analyzers

```
[INFO] Running 8 weighted analyzers...

BIAS ANALYZERS:
  ├── EconomicAnalyzer (35%): Analyzing 16 articles...
  │   └── Result: "Regulated Market Economy" → Score: -2.5
  ├── SocialAnalyzer (35%): Analyzing 16 articles...
  │   └── Result: "Mild Progressive" → Score: -2.5
  ├── NewsReportingAnalyzer (15%): Analyzing 16 news articles...
  │   └── Result: "Mild Left Reporting" → Score: -1.8
  │       ├── Story Selection: 3 left, 2 right, 11 neutral
  │       ├── Framing: 2 left, 1 right, 13 neutral
  │       └── Sourcing: 70% multi-sided
  └── EditorialBiasAnalyzer (15%): Analyzing 4 opinion articles...
      └── Result: "Mild Left Editorial Bias" → Score: -2.1
          ├── Clickbait: 1.2/10
          ├── Loaded Language: 2.8/10
          └── Direction: left (confidence: 0.65)

FACTUALITY ANALYZERS:
  ├── FactCheckSearcher (40%): Searching IFCN fact-checkers...
  │   └── Result: 1 failed fact check found → Score: 1.0/10
  ├── SourcingAnalyzer (25%): Analyzing hyperlinks...
  │   └── Result: Avg 2.3 sources/article, 68% credible → Score: 1.5/10
  ├── TransparencyAnalyzer (25%): Checking site metadata...
  │   └── Result: All disclosures present → Score: 0.0/10
  └── PropagandaAnalyzer (10%): Running DeBERTa SI+TC pipeline...
      └── Result: 2 instances detected → Score: 3.0/10

SUPPORTING DATA:
  ├── MediaTypeAnalyzer: "TV Station"
  ├── CountryFreedomAnalyzer: GB → "MOSTLY FREE" (87.18/100)
  └── TrafficLongevityAnalyzer: "High Traffic" + ">10 years" → 3 points
```

### Step 4: Calculate Weighted Scores

**Bias Calculation:**
```
(-2.5 × 0.35) + (-2.5 × 0.35) + (-1.8 × 0.15) + (-2.1 × 0.15)
= -0.875 + -0.875 + -0.27 + -0.315
= -2.335
→ Label: "LEFT-CENTER"
```

**Factuality Calculation:**
```
(1.0 × 0.40) + (1.5 × 0.25) + (0.0 × 0.25) + (3.0 × 0.10)
= 0.40 + 0.375 + 0.0 + 0.30
= 1.075
→ Label: "HIGH"
```

**Credibility Calculation:**
```
Factual Points (HIGH): +3
Bias Points (LEFT-CENTER): +2
Traffic Bonus: +3
Freedom Penalty: 0
─────────────────────
TOTAL: 8/10 → "HIGH CREDIBILITY"
```

### Step 5: Generate Final Report

```
Detailed Report for bbc.com
Bias Rating: LEFT-CENTER (-2.3)
Factual Reporting: HIGH (1.1)
Country: United Kingdom
MBFC's Country Freedom Rating: MOSTLY FREE
Media Type: TV Station
Traffic/Popularity: High Traffic
MBFC Credibility Rating: HIGH CREDIBILITY
```

---

## Project Structure

```
media-profiling/
|
+-- config.py                    # Configuration constants and scoring scales
|   +-- MBFC scoring constants
|   +-- Propaganda techniques (14 classes)
|   +-- Economic/Social/Editorial scales
|   +-- Model and training configurations
|
+-- analyzers.py                 # MBFC-compliant analysis components
|   +-- Bias Analyzers (Economic, Social, NewsReporting, Editorial)
|   +-- Factuality Analyzers (FactCheck, Sourcing, Transparency, Propaganda)
|   +-- IdeologyDecisionTreeAnalyzer (recursive question-based)
|   +-- ScoringCalculator
|
+-- editorial_bias_detection.py  # Editorial bias detection
|   +-- ClickbaitAnalyzer
|   +-- LoadedLanguageAnalyzer
|   +-- StructuredEditorialBiasAnalyzer
|
+-- scraper.py                   # Web scraping for articles and metadata
|   +-- MediaScraper
|   +-- Article dataclass
|   +-- SiteMetadata dataclass
|
+-- profiler.py                  # LangGraph orchestration workflow
|   +-- ProfilerState
|   +-- Pipeline nodes
|   +-- CLI interface
|
+-- localDetector.py             # DeBERTa inference pipeline
|   +-- LocalPropagandaDetector
|
+-- trainPipeline.py             # DeBERTa fine-tuning pipeline
|
+-- parser.py                    # MBFC website parser
|
+-- ideology_question_bank.json  # Comprehensive ideology question bank
|   +-- Economic System dimension
|   +-- Social Values dimension
|   +-- Academic references
|
+-- 2025.csv                     # Freedom Index dataset (181 countries)
|
+-- datasets/                    # SemEval 2020 Task 11 data
|   +-- train/
|   +-- dev/
|   +-- test/
|
+-- propaganda_models/           # Trained model outputs
    +-- si_model/
    +-- tc_model/
```

---

## References

### Methodology
- [Media Bias/Fact Check Methodology](https://mediabiasfactcheck.com/methodology/)
- [Freedom House - Freedom in the World](https://freedomhouse.org/report/freedom-world)
- [Reporters Without Borders - Press Freedom Index](https://rsf.org/en/index)

### Propaganda Detection
- [SemEval 2020 Task 11: Detection of Propaganda Techniques](https://propaganda.qcri.org/semeval2020-task11/)
- [DeBERTa: Decoding-enhanced BERT with Disentangled Attention](https://arxiv.org/abs/2006.03654)

### Editorial Bias Detection
- Recasens et al. (2013) - [Linguistic Models for Analyzing and Detecting Biased Language](https://web.stanford.edu/~jurafsky/pubs/neutrality.pdf)
- Chakraborty et al. (2016) - Stop Clickbait: Detecting and Preventing Clickbait in Online News
- [QCRI Analysis of Emotional Language](https://source.opennews.org/articles/analysis-emotional-language/)

### Political Science
- Academic references for ideology questions are embedded in `ideology_question_bank.json`

---

## License

MIT License
