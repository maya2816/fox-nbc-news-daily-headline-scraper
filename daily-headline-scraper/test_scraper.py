#!/usr/bin/env python3
"""
Quick test script to preview what headlines are being scraped.
Run this to see the output before running the full daily collector.

Output is displayed in the console AND saved to test_scraper_output.txt
"""

import sys
import random
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
log_print("[2] Testing NBC News homepage scraper...")
log_print("-" * 60)
try:
    nbc_headlines = scrape_headlines_nbcnews(verbose=True)
    log_print(f"\n✓ Successfully scraped {len(nbc_headlines)} headlines from NBC News homepage")
except Exception as e:
    log_print(f"\n✗ Error scraping NBC News homepage: {str(e)}")
    nbc_headlines = []
    import traceback
    log_print(traceback.format_exc())

# Simulate the balancing logic from collect_daily_headlines()
log_print("\n" + "=" * 60)
log_print("[3] Simulating Balanced Sampling Logic")
log_print("-" * 60)
min_headlines = min(len(fox_headlines), len(nbc_headlines))
log_print(f"Fox News scraped: {len(fox_headlines)} headlines")
log_print(f"NBC News scraped: {len(nbc_headlines)} headlines")
log_print(f"Minimum (min_headlines): {min_headlines} headlines")

# Combine and deduplicate NBC headlines (as done in the main collector)
log_print("\n" + "=" * 60)
log_print("[4] Combining and deduplicating NBC headlines...")
log_print("-" * 60)
nbc_all_headlines = nbc_homepage_headlines + nbc_latest_headlines
nbc_seen = set()
nbc_unique_headlines = []
for headline in nbc_all_headlines:
    normalized = headline.lower().strip()
    if normalized not in nbc_seen:
        nbc_seen.add(normalized)
        nbc_unique_headlines.append(headline)

log_print(f"NBC Homepage: {len(nbc_homepage_headlines)} headlines")
log_print(f"NBC Latest Stories: {len(nbc_latest_headlines)} headlines")
log_print(f"NBC Total (before dedup): {len(nbc_all_headlines)} headlines")
log_print(f"NBC Unique (after dedup): {len(nbc_unique_headlines)} headlines")
if len(nbc_all_headlines) > len(nbc_unique_headlines):
    duplicates = len(nbc_all_headlines) - len(nbc_unique_headlines)
    log_print(f"Duplicates removed: {duplicates} headlines")

log_print("\n" + "=" * 60)
log_print("Summary")
log_print("=" * 60)
log_print(f"Fox News scraped: {len(fox_headlines)} headlines")
log_print(f"NBC News scraped: {len(nbc_headlines)} headlines")
log_print(f"Minimum (min_headlines): {min_headlines} headlines")
log_print(f"\nAfter balancing:")
log_print(f"  Fox News: {len(fox_sampled)} headlines")
log_print(f"  NBC News: {len(nbc_sampled)} headlines")
log_print(f"  Total balanced: {len(fox_sampled) + len(nbc_sampled)} headlines")

# Calculate balance
if len(fox_sampled) + len(nbc_sampled) > 0:
    total = len(fox_sampled) + len(nbc_sampled)
    fox_pct = (len(fox_sampled) / total) * 100
    nbc_pct = (len(nbc_sampled) / total) * 100
    log_print(f"\nClass Balance (after balancing):")
    log_print(f"  Fox News: {fox_pct:.1f}%")
    log_print(f"  NBC News: {nbc_pct:.1f}%")
    if abs(fox_pct - nbc_pct) < 1:
        log_print(f"  ✓ Perfectly balanced!")
    else:
        log_print(f"  ⚠️  Slight imbalance detected")

if len(fox_sampled) > 0:
    log_print(f"\nFox News Headlines (sampled, first 10):")
    for i, headline in enumerate(fox_sampled[:10], 1):
        log_print(f"  {i}. {headline}")

if len(nbc_sampled) > 0:
    log_print(f"\nNBC News Headlines (sampled, first 10):")
    for i, headline in enumerate(nbc_sampled[:10], 1):
        log_print(f"  {i}. {headline}")

if len(fox_sampled) == 0 and len(nbc_sampled) == 0:
    log_print("\nWARNING: No headlines were scraped!")
    log_print("This could mean:")
    log_print("  1. The HTML structure has changed")
    log_print("  2. The website is blocking requests")
    log_print("  3. Network connectivity issues")
    log_print("  4. pandas/numpy compatibility issue (see error above)")
    log_print("\nConsider sending specific HTML components for debugging.")

log_print(f"\n\nFull output saved to: {output_file}")

