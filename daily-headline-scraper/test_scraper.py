#!/usr/bin/env python3
"""
Quick test script to preview what headlines are being scraped.
Run this to see the output before running the full daily collector.

Output is displayed in the console AND saved to test_scraper_output.txt
"""

import sys
from datetime import datetime
from daily_headline_collector import scrape_headlines_foxnews, scrape_headlines_nbcnews

# Create output file
output_file = "test_scraper_output.txt"

def log_print(*args, **kwargs):
    """Print to both console and file"""
    print(*args, **kwargs)
    with open(output_file, 'a', encoding='utf-8') as f:
        print(*args, **kwargs, file=f)

# Clear/create output file
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"Test Scraper Output - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 60 + "\n\n")

log_print("=" * 60)
log_print("Testing Headline Scrapers")
log_print("=" * 60)
log_print(f"\nOutput will be saved to: {output_file}")

log_print("\n[1] Testing Fox News scraper...")
log_print("-" * 60)
try:
    fox_headlines = scrape_headlines_foxnews(verbose=True)
    log_print(f"\n✓ Successfully scraped {len(fox_headlines)} headlines from Fox News")
except Exception as e:
    log_print(f"\n✗ Error scraping Fox News: {str(e)}")
    fox_headlines = []
    import traceback
    log_print(traceback.format_exc())

log_print("\n" + "=" * 60)
log_print("[2] Testing NBC News scraper...")
log_print("-" * 60)
try:
    nbc_headlines = scrape_headlines_nbcnews(verbose=True)
    log_print(f"\n✓ Successfully scraped {len(nbc_headlines)} headlines from NBC News")
except Exception as e:
    log_print(f"\n✗ Error scraping NBC News: {str(e)}")
    nbc_headlines = []
    import traceback
    log_print(traceback.format_exc())

log_print("\n" + "=" * 60)
log_print("Summary")
log_print("=" * 60)
log_print(f"Fox News: {len(fox_headlines)} headlines")
log_print(f"NBC News: {len(nbc_headlines)} headlines")
log_print(f"Total: {len(fox_headlines) + len(nbc_headlines)} headlines")

if len(fox_headlines) > 0:
    log_print(f"\nFox News Headlines (first 10):")
    for i, headline in enumerate(fox_headlines[:10], 1):
        log_print(f"  {i}. {headline}")

if len(nbc_headlines) > 0:
    log_print(f"\nNBC News Headlines (first 10):")
    for i, headline in enumerate(nbc_headlines[:10], 1):
        log_print(f"  {i}. {headline}")

if len(fox_headlines) == 0 and len(nbc_headlines) == 0:
    log_print("\n⚠️  WARNING: No headlines were scraped!")
    log_print("This could mean:")
    log_print("  1. The HTML structure has changed")
    log_print("  2. The website is blocking requests")
    log_print("  3. Network connectivity issues")
    log_print("  4. pandas/numpy compatibility issue (see error above)")
    log_print("\nConsider sending specific HTML components for debugging.")

log_print(f"\n\nFull output saved to: {output_file}")

