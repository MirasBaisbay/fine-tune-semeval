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

### refactored_analyzers.py - LLM-Based Analyzers

Modern analyzers using LangChain's structured output for type-safe LLM responses:

**Content Analyzers:**
- `OpinionAnalyzer` - Article type classification (News/Opinion/Satire/PR)
- `EditorialBiasAnalyzer` - LLM-based political bias detection
- `PseudoscienceAnalyzer` - Science misinformation detection

**Metadata Analyzers:**
- `TrafficLongevityAnalyzer` - Hybrid Tranco + WHOIS + LLM
- `MediaTypeAnalyzer` - Hybrid lookup + LLM classification

**Factuality Analyzers:**
- `FactCheckSearcher` - Multi-site fact-checker search + LLM parsing
- `SourcingAnalyzer` - Link extraction + LLM quality assessment

### parser.py - MBFC Website Parser

Specialized parser for scraping Media Bias/Fact Check website to collect source URLs.

---

## Refactored Analyzer Flow Diagrams

### TrafficLongevityAnalyzer

Hybrid deterministic + LLM approach for traffic and domain age analysis.

```
analyze(domain)
    │
    ├─► 1. WHOIS Lookup (always runs)
    │       └─► Extract creation_date → Calculate age_years
    │
    ├─► 2. Tranco Lookup (O(1) dict lookup)
    │       │   Source: https://tranco-list.eu/
    │       │   - Top 1M domains ranked by popularity
    │       │   - Auto-downloads if missing
    │       │
    │       ├─► Found?
    │       │       ├─► rank < 10,000    → HIGH traffic
    │       │       ├─► rank < 100,000   → MEDIUM traffic
    │       │       ├─► rank < 1,000,000 → LOW traffic
    │       │       └─► Return with confidence=1.0, source=TRANCO
    │       │
    │       └─► Not found? → Continue to step 3
    │
    └─► 3. LLM Fallback
            ├─► Search: "{domain} traffic stats similarweb hypestat semrush"
            ├─► Combine top 5 result snippets
            └─► Parse with structured LLM output → TrafficEstimate
                    ├─► traffic_tier: HIGH/MEDIUM/LOW/MINIMAL/UNKNOWN
                    ├─► monthly_visits_estimate (if found)
                    ├─► confidence: 0.0-1.0
                    └─► reasoning

OUTPUT: TrafficData
    ├── domain, creation_date, age_years
    ├── traffic_tier, traffic_confidence
    ├── traffic_source: TRANCO | LLM | FALLBACK
    ├── tranco_rank (if available)
    └── whois_success, whois_error
```

### MediaTypeAnalyzer

Hybrid lookup table + LLM approach for media type classification.

```
analyze(url_or_domain)
    │
    ├─► 1. Known Types Lookup (O(1) dict)
    │       │   Source: known_media_types.csv
    │       │   - Pre-classified major outlets
    │       │   - Maps domain → MediaType enum
    │       │
    │       ├─► Found?
    │       │       └─► Return with confidence=1.0, source=LOOKUP
    │       │
    │       └─► Not found? → Continue to step 2
    │
    └─► 2. LLM Classification
            ├─► Search: '"{domain}" type of media outlet newspaper television website magazine'
            ├─► Fallback: "{site_name} wikipedia media company"
            └─► Parse with structured LLM output → MediaTypeLLMOutput
                    ├─► media_type: TV/NEWSPAPER/WEBSITE/MAGAZINE/RADIO/NEWS_AGENCY/BLOG/PODCAST/STREAMING/UNKNOWN
                    ├─► confidence: 0.0-1.0
                    └─► reasoning

OUTPUT: MediaTypeClassification
    ├── media_type: MediaType enum
    ├── confidence: 0.0-1.0
    ├── source: LOOKUP | LLM | FALLBACK
    └── reasoning
```

### FactCheckSearcher (40% of Factuality Score)

Multi-site search + LLM parsing for fact-check findings.

```
analyze(url_or_domain, outlet_name?)
    │
    ├─► 1. Extract Domain & Outlet Name
    │       ├─► "nytimes.com" → "New York Times"
    │       └─► Uses known_names dict or generates from domain
    │
    ├─► 2. Search 5 Fact-Checker Sites
    │       │   Sites:
    │       │   ├── mediabiasfactcheck.com
    │       │   ├── politifact.com
    │       │   ├── snopes.com
    │       │   ├── factcheck.org
    │       │   └── fullfact.org
    │       │
    │       │   Query format:
    │       │   site:{site} "{domain}" OR "{outlet_name}"
    │       │
    │       └─► Collect up to 3 results per site → Combine snippets
    │
    ├─► 3. LLM Parsing
    │       └─► Parse snippets → FactCheckLLMOutput
    │               ├─► findings: List[FactCheckFinding]
    │               │       ├── source_site (PolitiFact, Snopes, etc.)
    │               │       ├── claim_summary
    │               │       ├── verdict: TRUE/MOSTLY_TRUE/HALF_TRUE/MIXED/
    │               │       │            MOSTLY_FALSE/FALSE/PANTS_ON_FIRE/
    │               │       │            MISLEADING/UNPROVEN/NOT_RATED
    │               │       └── url (if available)
    │               ├─► failed_count (FALSE, MOSTLY_FALSE, PANTS_ON_FIRE, MISLEADING)
    │               ├─► total_count
    │               └─► confidence, reasoning
    │
    └─► 4. Score Calculation
            ├─► 0 failed checks    → 0.0 (excellent)
            ├─► 1-2 failed checks  → 2.0-4.0
            ├─► 3-5 failed checks  → 5.0-7.0
            ├─► 6+ failed checks   → 8.0-10.0 (very poor)
            └─► No data found      → 5.0 (neutral)

OUTPUT: FactCheckAnalysisResult
    ├── domain, outlet_name
    ├── failed_checks_count, total_checks_count
    ├── score: 0.0-10.0
    ├── source: SEARCH | FALLBACK
    ├── findings: List[FactCheckFinding]
    └── confidence, reasoning
```

### SourcingAnalyzer (25% of Factuality Score)

Link extraction + LLM quality assessment for source evaluation.

```
analyze(articles: List[{text}])
    │
    ├─► 1. Extract Links from All Articles
    │       └─► Regex: https?://[^\s<>"')\]]+
    │
    ├─► 2. Extract Unique Domains
    │       │   Filter out social media:
    │       │   ├── twitter.com, x.com
    │       │   ├── facebook.com, instagram.com
    │       │   ├── youtube.com, tiktok.com
    │       │   ├── linkedin.com, reddit.com
    │       │   └── t.co (Twitter short links)
    │       │
    │       └─► No domains found? → Return score=5.0 (neutral)
    │
    └─► 3. LLM Quality Assessment
            └─► Assess each domain → SourcingLLMOutput
                    ├─► sources_assessed: List[SourceAssessment]
                    │       ├── domain
                    │       ├── quality: PRIMARY/WIRE_SERVICE/MAJOR_OUTLET/
                    │       │            CREDIBLE/UNKNOWN/QUESTIONABLE
                    │       └── reasoning
                    ├─► overall_quality_score: 0.0-10.0
                    ├─► has_primary_sources: bool
                    ├─► has_wire_services: bool
                    └─► overall_assessment

Quality Tiers:
    PRIMARY       → .gov, .edu, official sources, research papers
    WIRE_SERVICE  → Reuters, AP, AFP, UPI
    MAJOR_OUTLET  → NYT, BBC, WSJ, WaPo, Guardian, CNN
    CREDIBLE      → Regional papers, trade publications
    UNKNOWN       → Unfamiliar domains
    QUESTIONABLE  → Known unreliable sources

OUTPUT: SourcingAnalysisResult
    ├── score: 0.0-10.0 (0=excellent, 10=poor)
    ├── avg_sources_per_article
    ├── total_sources_found, unique_domains
    ├── has_hyperlinks, has_primary_sources, has_wire_services
    ├── source_assessments: List[SourceAssessment]
    └── confidence, reasoning
```

### EditorialBiasAnalyzer (Refactored - LLM-Based)

Replaces keyword/lexicon matching with comprehensive LLM content analysis.

```
analyze(articles: List[{title, text}], url_or_domain?, outlet_name?)
    │
    ├─► 1. Format Articles for Analysis
    │       └─► Combine title + first 2000 chars of each article
    │
    └─► 2. LLM Analysis with MBFC Methodology
            │
            │   System Prompt encodes:
            │   ├── Bias Scale: -10 (far left) to +10 (far right)
            │   ├── Policy Domain Indicators:
            │   │       ├── Economic Policy (taxes, regulation, unions)
            │   │       ├── Social Issues (abortion, LGBTQ+, guns)
            │   │       ├── Environmental Policy (climate, regulations)
            │   │       ├── Healthcare (universal vs private)
            │   │       ├── Immigration (pathways vs enforcement)
            │   │       └── Gun Rights (control vs 2A)
            │   ├── Loaded Language Detection:
            │   │       ├── LEFT: "regime", "far-right", "fascist", "climate denier"
            │   │       └── RIGHT: "radical left", "woke", "cancel culture", "fake news"
            │   └── Story Selection Bias patterns
            │
            └─► Parse → EditorialBiasLLMOutput
                    ├─► overall_bias: EXTREME_LEFT/LEFT/LEFT_CENTER/CENTER/
                    │                 RIGHT_CENTER/RIGHT/EXTREME_RIGHT
                    ├─► bias_score: -10.0 to +10.0
                    ├─► policy_positions: List[PolicyPosition]
                    │       ├── domain: ECONOMIC/SOCIAL/ENVIRONMENTAL/HEALTHCARE/
                    │       │           IMMIGRATION/FOREIGN_POLICY/GUN_RIGHTS/EDUCATION
                    │       ├── leaning: BiasDirection
                    │       ├── indicators: List[str]
                    │       └── confidence
                    ├─► uses_loaded_language: bool
                    ├─► loaded_language_examples: List[str]
                    ├─► story_selection_bias: str (optional)
                    └─► confidence, reasoning

Score to Label Mapping:
    score <= -7  → "Left"
    -7 < score <= -3 → "Left-Center"
    -3 < score <= 3  → "Center"
    3 < score <= 7   → "Right-Center"
    score > 7    → "Right"

OUTPUT: EditorialBiasResult
    ├── domain, outlet_name
    ├── overall_bias: BiasDirection
    ├── bias_score: -10.0 to +10.0
    ├── mbfc_label: "Left"/"Left-Center"/"Center"/"Right-Center"/"Right"
    ├── policy_positions, loaded_language_examples
    ├── articles_analyzed
    └── confidence, reasoning
```

### PseudoscienceAnalyzer (New)

LLM-based detection of pseudoscience and conspiracy content.

```
analyze(articles: List[{title, text}], url_or_domain?, outlet_name?)
    │
    ├─► 1. Format Articles for Analysis
    │       └─► Combine title + first 2000 chars of each article
    │
    └─► 2. LLM Analysis with Scientific Consensus
            │
            │   System Prompt includes:
            │   ├── Pseudoscience Definition
            │   │       "Claims presented as scientific but incompatible
            │   │        with scientific method - unproven, untestable,
            │   │        or contradicting scientific consensus"
            │   │
            │   ├── Categories to Detect:
            │   │   HEALTH:
            │   │   ├── Anti-Vaccination (vaccines cause autism, etc.)
            │   │   ├── Alternative Medicine (homeopathy, crystal healing)
            │   │   ├── Alternative Cancer Treatments
            │   │   ├── COVID-19 Misinformation
            │   │   └── Detoxification Claims
            │   │
            │   │   CLIMATE/ENVIRONMENTAL:
            │   │   ├── Climate Change Denialism
            │   │   ├── 5G Health Conspiracy
            │   │   ├── Chemtrails
            │   │   └── GMO Danger Claims
            │   │
            │   │   PARANORMAL:
            │   │   ├── Astrology, Psychic Claims
            │   │   └── Faith Healing
            │   │
            │   │   CONSPIRACY:
            │   │   ├── Flat Earth, Moon Landing Hoax
            │   │   └── QAnon
            │   │
            │   └── Severity Assessment:
            │           PROMOTES → Actively promotes as fact
            │           PRESENTS_UNCRITICALLY → Reports without context
            │           MIXED → Inconsistent treatment
            │           NONE_DETECTED → Respects scientific consensus
            │
            └─► Parse → PseudoscienceLLMOutput
                    ├─► indicators: List[PseudoscienceIndicator]
                    │       ├── category: PseudoscienceCategory
                    │       ├── severity: PseudoscienceSeverity
                    │       ├── evidence: str
                    │       └── scientific_consensus: str
                    ├─► promotes_pseudoscience: bool
                    ├─► overall_severity: PseudoscienceSeverity
                    ├─► science_reporting_quality: 0.0-10.0
                    ├─► respects_scientific_consensus: bool
                    └─► confidence, reasoning

OUTPUT: PseudoscienceAnalysisResult
    ├── domain, outlet_name
    ├── score: 0.0-10.0 (0=pro-science, 10=promotes pseudoscience)
    ├── promotes_pseudoscience: bool
    ├── overall_severity: PROMOTES/PRESENTS_UNCRITICALLY/MIXED/NONE_DETECTED
    ├── categories_found: List[PseudoscienceCategory]
    ├── indicators: List[PseudoscienceIndicator]
    ├── respects_scientific_consensus: bool
    ├── articles_analyzed
    └── confidence, reasoning
```

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
│
├── config.py                    # Configuration constants and scoring scales
│   ├── MBFC scoring constants
│   ├── Propaganda techniques (14 classes)
│   ├── Economic/Social/Editorial scales
│   └── Model and training configurations
│
├── schemas.py                   # Pydantic v2 schemas for structured LLM outputs
│   ├── Article Classification (ArticleType, ArticleClassification)
│   ├── Media Type (MediaType, MediaTypeClassification)
│   ├── Traffic/Longevity (TrafficTier, TrafficData)
│   ├── Fact Check (FactCheckVerdict, FactCheckFinding, FactCheckAnalysisResult)
│   ├── Sourcing (SourceQuality, SourceAssessment, SourcingAnalysisResult)
│   ├── Editorial Bias (BiasDirection, PolicyPosition, EditorialBiasResult)
│   └── Pseudoscience (PseudoscienceCategory, PseudoscienceIndicator, PseudoscienceAnalysisResult)
│
├── refactored_analyzers.py      # LLM-based analyzers with structured output
│   ├── OpinionAnalyzer (article type classification)
│   ├── TrafficLongevityAnalyzer (hybrid Tranco + WHOIS + LLM)
│   ├── MediaTypeAnalyzer (hybrid lookup + LLM)
│   ├── FactCheckSearcher (multi-site search + LLM parsing)
│   ├── SourcingAnalyzer (link extraction + LLM quality assessment)
│   ├── EditorialBiasAnalyzer (LLM-based political bias)
│   └── PseudoscienceAnalyzer (LLM-based pseudoscience detection)
│
├── analyzers.py                 # MBFC-compliant analysis components
│   ├── Bias Analyzers (Economic, Social, NewsReporting, Editorial)
│   ├── Factuality Analyzers (FactCheck, Sourcing, Transparency, Propaganda)
│   ├── IdeologyDecisionTreeAnalyzer (recursive question-based)
│   └── ScoringCalculator
│
├── editorial_bias_detection.py  # Legacy editorial bias detection (rule-based)
│   ├── ClickbaitAnalyzer
│   ├── LoadedLanguageAnalyzer
│   └── StructuredEditorialBiasAnalyzer
│
├── scraper.py                   # Web scraping for articles and metadata
│   ├── MediaScraper
│   ├── Article dataclass
│   └── SiteMetadata dataclass
│
├── profiler.py                  # LangGraph orchestration workflow
│   ├── ProfilerState
│   ├── Pipeline nodes
│   └── CLI interface
│
├── localDetector.py             # DeBERTa inference pipeline
│   └── LocalPropagandaDetector
│
├── trainPipeline.py             # DeBERTa fine-tuning pipeline
│
├── parser.py                    # MBFC website parser
│
├── ideology_question_bank.json  # Comprehensive ideology question bank
│   ├── Economic System dimension
│   ├── Social Values dimension
│   └── Academic references
│
├── known_media_types.csv        # Pre-classified media outlet types
│
├── tranco_top1m.csv             # Tranco top 1M domains (auto-downloaded)
│
├── 2025.csv                     # Freedom Index dataset (181 countries)
│
├── verify_*.py                  # Verification scripts for analyzers
│   ├── verify_factcheck.py
│   ├── verify_sourcing.py
│   ├── verify_editorial_bias.py
│   └── verify_pseudoscience.py
│
├── datasets/                    # SemEval 2020 Task 11 data
│   ├── train/
│   ├── dev/
│   └── test/
│
└── propaganda_models/           # Trained model outputs
    ├── si_model/
    └── tc_model/
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
