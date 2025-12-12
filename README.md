# Fox-NBC News Daily Headline Scraper

**Part of CIS 4190: Applied Machine Learning - Final Project (Exploratory Component)**

Automated daily headline scraper that collects headlines from Fox News and NBC News homepages. The script runs automatically every day via GitHub Actions and combines new headlines with existing datasets.

## Overview

This scraper extracts headline titles (not URLs) from:
- [Fox News Homepage](https://www.foxnews.com)
- [NBC News Homepage](https://www.nbcnews.com)

The script uses custom scraping functions tailored to each site's HTML structure for reliable extraction. It automatically runs daily at 2:00 AM UTC via GitHub Actions, collects new headlines, integrates them with existing data, removes duplicates, and saves the updated dataset.

## Data

### 1. `data/scraped_headlines_data.csv`
**Static dataset** - Contains headlines scraped from project-provided URLs (`data/url_only_data.csv`). This file remains **unchanged** (read-only).

### 2. `data/daily_updated_headlines_data.csv`
**Dynamic dataset** - Contains all headlines:
- Original headlines from `scraped_headlines_data.csv` (with `collection_date='initial'`)
- All daily collected headlines (with actual collection dates in YYYY-MM-DD format)
- Automatically deduplicated (case-insensitive headline matching)
- **Updated each time the scraper runs**

## Repository Structure

```
fox-nbc-news-daily-scraper/
├── data/
│   ├── scraped_headlines_data.csv          # Original headlines (static)
│   ├── daily_updated_headlines_data.csv    # Integrated dataset (dynamic)
│   ├── url_only_data.csv                   # Project-provided URLs
│   └── urls_with_sources.csv               # URLs with source labels
├── daily-headline-scraper/
│   ├── daily_headline_collector.py         # Main scraper script
│   ├── test_scraper.py                     # Test script to preview scraped headlines
│   └── test_scraper_output.txt             # Test output file
├── .github/
│   └── workflows/
│       └── daily-collector.yml             # GitHub Actions workflow
└── README.md
```

## Key Files & Functions

### `daily-headline-scraper/daily_headline_collector.py`

**Main Functions:**

1. **`scrape_headlines_foxnews(url, max_retries, delay, verbose)`**
   - Custom scraper for Fox News homepage
   - Extracts headlines from multiple page sections (featured articles, thumbs, sidebar, collections)
   - Returns: List of headline strings

2. **`scrape_headlines_nbcnews(url, max_retries, delay, verbose)`**
   - Custom scraper for NBC News homepage
   - Uses multiple extraction strategies for different page layouts
   - Returns: List of headline strings

3. **`collect_daily_headlines(target_date)`**
   - Orchestrates daily collection from both sources
   - Adds `collection_date` to all headlines
   - Returns: DataFrame with columns: `headline`, `source`, `collection_date`

4. **`integrate_with_existing_dataset(daily_headlines, original_dataset_path, integrated_dataset_path)`**
   - Loads original dataset (`data/scraped_headlines_data.csv`)
   - Loads existing integrated dataset (`data/daily_updated_headlines_data.csv`)
   - Combines all datasets
   - Removes duplicates (case-insensitive headline matching)
   - Saves updated integrated dataset

5. **`main()`**
   - Entry point for the script
   - Executes full collection and integration workflow

## Usage

### Manual Execution
```bash
cd daily-headline-scraper
python daily_headline_collector.py
```

### Test Scraper
```bash
cd daily-headline-scraper
python test_scraper.py
```
Output is displayed in console and saved to `test_scraper_output.txt`.

### Automated Execution
The scraper runs automatically via GitHub Actions:
- **Schedule:** Daily at 2:00 AM UTC
- **Workflow:** `.github/workflows/daily-collector.yml`
- **Actions:** Collects headlines → Integrates with datasets → Commits results

## Dependencies

```bash
pip install pandas requests beautifulsoup4 numpy
```

## Data Schema

All datasets use the following columns:
- `headline`: Headline text (string)
- `source`: News source (`FoxNews` or `NBC`)
- `collection_date`: Date in YYYY-MM-DD format (or `'initial'` for original data)

## Author

Maya Kfir - CIS 4190 Final Project

