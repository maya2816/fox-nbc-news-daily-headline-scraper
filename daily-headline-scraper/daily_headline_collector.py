#!/usr/bin/env python3
"""
Daily Headline Collector Script
--------------------------------
- Automated script to collect headlines from Fox News and NBC News homepages daily.
- Exploratory component 'dataset' for CIS 4190 Final Project.

This script can be run:
- Manually: python daily_headline_collector.py
- Via GitHub Actions: See .github/workflows/daily-collector.yml
- Via cron/Task Scheduler: Schedule to run daily

Functions:
- scrape_headlines_foxnews() : Custom scraping tailored to Fox News HTML structure.
- scrape_headlines_nbcnews() : Custom scraping tailored to NBC News HTML structure.
- collect_daily_headlines() : Collect headlines from Fox News and NBC News homepages for today.
- integrate_with_existing_dataset() : Integrate collected headlines with existing headlines dataset.

Author: Maya Kfir (CIS 4190 Final Project)
"""

import os
import sys
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Determine base directory (repository root)
# If running from daily-headline-scraper/, go up one level
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == 'daily-headline-scraper':
    BASE_DIR = os.path.dirname(SCRIPT_DIR)
else:
    BASE_DIR = SCRIPT_DIR

DATA_DIR = os.path.join(BASE_DIR, 'data')


def scrape_headlines_foxnews(url="https://www.foxnews.com", max_retries=3, delay=1, verbose=True):
    """
    Scrape headline titles from Fox News homepage, custom function tailored to
    Fox News HTML structure.
    Custom function tailored to Fox News HTML structure.
    
    Args:
        url: Fox News homepage URL (default: https://www.foxnews.com)
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Delay between retries in seconds (default: 1)
        verbose: Print scraped headlines (default: True)
    
    Returns:
        list: List of headline strings (titles only, no URLs)
    """
    headlines = []
    
    for attempt in range(max_retries):
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            
            # Check if request was successful
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    print(f"  Error: Failed to fetch Fox News (status {response.status_code})")
                    return headlines
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract headlines from multiple sections on Fox News homepage
            
            # 1. Main featured article (story-1) - First article
            # Structure: <article class="article story-1"> -> <div class="info"> -> <header class="info-header"> -> <h3 class="title"> -> <a>
            main_articles = soup.find_all('article', class_=lambda x: x and 'article' in x and 'story-1' in x)
            for article in main_articles:
                title_elem = article.find('h3', class_='title')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        headline_text = link.get_text(strip=True)
                        if headline_text and len(headline_text) > 10:  # Basic validation
                            headlines.append(headline_text)
            
            # 2. Articles in thumbs-2-7 section (articles 2-7)
            # Structure: <div class="thumbs-2-7"> -> <article> -> <h3 class="title"> -> <a>
            thumbs_section = soup.find('div', class_='thumbs-2-7')
            if thumbs_section:
                articles = thumbs_section.find_all('article')
                for article in articles:
                    title_elem = article.find('h3', class_='title')
                    if title_elem:
                        link = title_elem.find('a')
                        if link:
                            headline_text = link.get_text(strip=True)
                            if headline_text and len(headline_text) > 10:
                                headlines.append(headline_text)
            
            # 3. Articles in region-content-sidebar-secondary
            # Structure: <div class="region-content-sidebar-secondary"> -> <article> -> <h3 class="title"> -> <a>
            sidebar_section = soup.find('div', class_='region-content-sidebar-secondary')
            if sidebar_section:
                articles = sidebar_section.find_all('article')
                for article in articles:
                    title_elem = article.find('h3', class_='title')
                    if title_elem:
                        link = title_elem.find('a')
                        if link:
                            headline_text = link.get_text(strip=True)
                            if headline_text and len(headline_text) > 10:
                                headlines.append(headline_text)
            
            # 4. Articles in collection sections (economy, world, etc.)
            # Structure: <section class="collection collection-section ..."> -> <article> -> <h3 class="title"> -> <a>
            collection_sections = soup.find_all('section', class_=lambda x: x and 'collection' in x and 'collection-section' in x)
            for section in collection_sections:
                articles = section.find_all('article')
                for article in articles:
                    title_elem = article.find('h3', class_='title')
                    if title_elem:
                        link = title_elem.find('a')
                        if link:
                            headline_text = link.get_text(strip=True)
                            if headline_text and len(headline_text) > 10:
                                headlines.append(headline_text)
            
            # 5. Additional articles with info-header structure
            # Fallback: Find all articles with info-header -> h3.title -> a
            all_info_headers = soup.find_all('header', class_='info-header')
            for header in all_info_headers:
                title_elem = header.find('h3', class_='title')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        headline_text = link.get_text(strip=True)
                        if headline_text and len(headline_text) > 10:
                            headlines.append(headline_text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_headlines = []
            for headline in headlines:
                # Normalize for comparison (lowercase, strip)
                normalized = headline.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    unique_headlines.append(headline)
            
            print(f"  Successfully scraped {len(unique_headlines)} unique headlines from Fox News")
            
            # Display scraped headlines if verbose
            if verbose and unique_headlines:
                print(f"\n  Sample headlines from Fox News (showing first 5):")
                for i, headline in enumerate(unique_headlines[:5], 1):
                    print(f"    {i}. {headline[:80]}{'...' if len(headline) > 80 else ''}")
                if len(unique_headlines) > 5:
                    print(f"    ... and {len(unique_headlines) - 5} more")
            
            return unique_headlines
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} for Fox News...")
                time.sleep(delay)
                continue
            else:
                print(f"  Error: Failed to fetch Fox News after {max_retries} attempts: {str(e)}")
                return headlines
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} for Fox News...")
                time.sleep(delay)
                continue
            else:
                print(f"  Error: Unexpected error scraping Fox News: {str(e)}")
                return headlines
    
    return headlines


def scrape_headlines_nbcnews(url="https://www.nbcnews.com", max_retries=3, delay=1, verbose=True):
    """
    Scrape headline titles from NBC News homepage.
    Custom function tailored to NBC News HTML structure.
    
    Args:
        url: NBC News homepage URL (default: https://www.nbcnews.com)
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Delay between retries in seconds (default: 1)
        verbose: Print scraped headlines (default: True)
    
    Returns:
        list: List of headline strings (titles only, no URLs)
    """
    headlines = []
    
    # Keywords to exclude (sponsored content, image credits, navigation, etc.)
    exclude_keywords = [
        'promotion', 'sponsored', 'advertisement', 'advert', 'commercial',
        'getty images', 'via ap', 'via reuters', 'via getty', 'photo by',
        'photographer', 'credit:', 'image credit', 'nbc news sitemap',
        'site map', 'closed captioning', 'culture and trends', 'business and tech',
        'health and science', 'most popular', 'editors\' picks', 'dallas-fort worth',
        'washington, d.c.', 'nbc asian america', 'special features', 'next steps for vets',
        'nbc news site map', 'live', 'trump admin', 'sherrone moore charges',
        'washington floods', 'tina peters pardon', 'house oversight committee',
        'andrew caballero-reynolds', 'saul loeb', 'joe raedle', 'alex brandon',
        'win mcnamee', 'luke hales', 'anatolii stepanov', 'al drago', 'alberto cassani',
        'tobias schwartz', 'mykal mceldowney', 'usa today network', 'via imagn',
        'tommy forbes', 'bango studios', 'justine goode', 'anthony behar', 'sipa usa',
        'stuart cahill', 'the boston herald', 'via ap, pool', 'minh connors',
        'charles krupa', 'kevin sabitus', 'gareth cattermole', 'tas rights management',
        'abdalhkem abu riash', 'anadolu via getty', 'vivian le', 'smirnoff',
        'williams sonoma', 'quiksilver', 'acne studios', 'amazon', 'harry rabinowitz',
        'michael owens', 'rick egan', 'pool via ap', 'courtesy of', '/ nbc',
        'nbc news', 'nbc', 'the injury analysts', 'falcons vs buccaneers recap',
        'tristan jarry trade', 'freddie kitchens fired', 't.j. watt injury',
        'artificial intelligence', 'nascar antitrust settlement', 'gas explosion',
        'live hand grenade', 'obamacare premium', 'republican-led house',
        'justice department', 'the risk of ai', 'a health care', 'pastors and prey',
        'u.s. offers', 'iran arrests', 'king charles to', 'germany summons',
        'federal reserve', 'senators ask', 'monthly tariff', 'reddit challenges',
        'triple-negative breast', 'fda proposes', 'eurovision champion',
        'marvelous mrs. maisel', 'talking shop', 'i\'ve tested', 'beef tallow',
        'schmidt\'s', 'salt & stone', 'native', 'jelly roll says'
    ]
    
    def is_valid_headline(text):
        """Check if text is a valid headline (not sponsored, credit, etc.)"""
        if not text or len(text) < 15 or len(text) > 200:
            return False
        
        text_lower = text.lower().strip()
        
        # Must have multiple words
        if ' ' not in text_lower:
            return False
        
        # Exclude if contains exclude keywords
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        
        # Exclude if looks like image credit (contains "/", "via", photographer names)
        if any(pattern in text_lower for pattern in [' / ', ' via ', 'photo by', 'credit:', 'getty', 'ap photo']):
            return False
        
        # Exclude if it's just a name (no verbs, articles, etc.)
        # Simple heuristic: if it's very short and has no common words
        if len(text.split()) <= 3 and not any(word in text_lower for word in ['the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or']):
            return False
        
        return True
    
    for attempt in range(max_retries):
        try:
            # Add headers to mimic a browser request
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            
            # Check if request was successful
            if response.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
                else:
                    print(f"  Error: Failed to fetch NBC News (status {response.status_code})")
                    return headlines
            
            # Parse HTML
            soup = BeautifulSoup(response.text, "html.parser")
            
            # 1. Main headline components: <h2 class="storyline__headline founders-cond fw6 lead"> or <h2 class="storyline__headline founders-cond fw6 large">
            main_headlines = soup.find_all('h2', class_=lambda x: x and 'storyline__headline' in x)
            for h2 in main_headlines:
                link = h2.find('a')
                if link:
                    headline_text = link.get_text(strip=True)
                    if is_valid_headline(headline_text):
                        headlines.append(headline_text)
            
            # 2. Latest News section: <h2 class="styles_teaseTitle__ClSV0">
            latest_news = soup.find_all('h2', class_='styles_teaseTitle__ClSV0')
            for h2 in latest_news:
                link = h2.find('a')
                if link:
                    headline_text = link.get_text(strip=True)
                    if is_valid_headline(headline_text):
                        headlines.append(headline_text)
            
            # 3. Topic sections (Politics, U.S. news, etc.): <h2 class="multistoryline__headline founders-cond fw6 large noBottomSpace">
            topic_headlines = soup.find_all('h2', class_=lambda x: x and 'multistoryline__headline' in x)
            for h2 in topic_headlines:
                link = h2.find('a')
                if link:
                    headline_text = link.get_text(strip=True)
                    if is_valid_headline(headline_text):
                        headlines.append(headline_text)
            
            # 4. Additional headlines in sections with storyline class
            storyline_sections = soup.find_all('section', class_=lambda x: x and 'storyline' in x)
            for section in storyline_sections:
                # Look for h2 with headline classes
                h2_tags = section.find_all('h2', class_=lambda x: x and ('headline' in x.lower() or 'storyline' in x.lower()))
                for h2 in h2_tags:
                    link = h2.find('a')
                    if link:
                        headline_text = link.get_text(strip=True)
                        if is_valid_headline(headline_text):
                            headlines.append(headline_text)
            
            # 5. Headlines in package sections (multi-storyline packages)
            package_sections = soup.find_all('section', class_=lambda x: x and 'pkg' in x and 'multi-storyline' in x)
            for section in package_sections:
                h2_tags = section.find_all('h2', class_=lambda x: x and 'headline' in x.lower())
                for h2 in h2_tags:
                    link = h2.find('a')
                    if link:
                        headline_text = link.get_text(strip=True)
                        if is_valid_headline(headline_text):
                            headlines.append(headline_text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_headlines = []
            for headline in headlines:
                # Normalize for comparison (lowercase, strip)
                normalized = headline.lower().strip()
                if normalized not in seen:
                    seen.add(normalized)
                    unique_headlines.append(headline)
            
            print(f"  Successfully scraped {len(unique_headlines)} unique headlines from NBC News")
            
            # Display scraped headlines if verbose
            if verbose and unique_headlines:
                print(f"\n  Sample headlines from NBC News (showing first 5):")
                for i, headline in enumerate(unique_headlines[:5], 1):
                    print(f"    {i}. {headline[:80]}{'...' if len(headline) > 80 else ''}")
                if len(unique_headlines) > 5:
                    print(f"    ... and {len(unique_headlines) - 5} more")
            
            return unique_headlines
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} for NBC News...")
                time.sleep(delay)
                continue
            else:
                print(f"  Error: Failed to fetch NBC News after {max_retries} attempts: {str(e)}")
                return headlines
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  Retry {attempt + 1}/{max_retries} for NBC News...")
                time.sleep(delay)
                continue
            else:
                print(f"  Error: Unexpected error scraping NBC News: {str(e)}")
                return headlines
    
    return headlines


def collect_daily_headlines(target_date=None):
    """
    Collect headlines from Fox News and NBC News homepages for today.
    
    Args:
        target_date: Date to use for collection_date (datetime object). If None, uses today.
    
    Returns:
        DataFrame with collected headlines (columns: headline, source, collection_date)
    """
    if target_date is None:
        target_date = datetime.now()
    
    print("=" * 60)
    print("Daily Headline Collector")
    print("=" * 60)
    print(f"\nCollection Date: {target_date.strftime('%Y-%m-%d')}")
    print(f"Time: {target_date.strftime('%H:%M:%S')}")
    
    collected_headlines = []
    collected_sources = []
    collection_dates = []
    
    # Scrape Fox News
    print("\n[1/2] Scraping Fox News homepage...")
    fox_headlines = scrape_headlines_foxnews()
    for headline in fox_headlines:
        collected_headlines.append(headline)
        collected_sources.append('FoxNews')
        collection_dates.append(target_date.strftime('%Y-%m-%d'))
    
    # Small delay between requests
    time.sleep(2)
    
    # Scrape NBC News
    print("\n[2/2] Scraping NBC News homepage...")
    nbc_headlines = scrape_headlines_nbcnews()
    for headline in nbc_headlines:
        collected_headlines.append(headline)
        collected_sources.append('NBC')
        collection_dates.append(target_date.strftime('%Y-%m-%d'))
    
    # Create DataFrame
    if collected_headlines:
        new_df = pd.DataFrame({
            'headline': collected_headlines,
            'source': collected_sources,
            'collection_date': collection_dates
        })
        
        print(f"\n" + "=" * 60)
        print("Collection Summary")
        print("=" * 60)
        print(f"   Total headlines collected: {len(new_df)}")
        print(f"   Fox News: {len(new_df[new_df['source'] == 'FoxNews'])}")
        print(f"   NBC News: {len(new_df[new_df['source'] == 'NBC'])}")
        
        return new_df
    else:
        print("\nNo headlines were successfully collected.")
        return pd.DataFrame(columns=['headline', 'source', 'collection_date'])


def integrate_with_existing_dataset(daily_headlines,
                                    original_dataset_path=None, 
                                    integrated_dataset_path=None):
    """
    Integrate collected headlines with existing dataset.
    - Loads original dataset (data/scraped_headlines_data.csv) - this file remains unchanged
    - Loads integrated dataset (data/daily_updated_headlines_data.csv) if it exists
    - Combines original + existing integrated + new daily headlines
    - Removes duplicates based on headline text (case-insensitive)
    - Adds collection_date to all entries
    - Saves updated integrated dataset to data/daily_updated_headlines_data.csv
    
    Args:
        daily_headlines: DataFrame with new headlines (columns: headline, source, collection_date)
        original_dataset_path: Path to original dataset (default: data/scraped_headlines_data.csv)
        integrated_dataset_path: Path to integrated/merged dataset (default: data/daily_updated_headlines_data.csv)
    
    Returns:
        DataFrame: Combined dataset with no duplicates
    """
    # Set default paths if not provided
    if original_dataset_path is None:
        original_dataset_path = os.path.join(DATA_DIR, 'scraped_headlines_data.csv')
    if integrated_dataset_path is None:
        integrated_dataset_path = os.path.join(DATA_DIR, 'daily_updated_headlines_data.csv')
    
    if len(daily_headlines) == 0:
        print("\nNo new headlines to integrate.")
        return None
    
    print("\n" + "=" * 60)
    print("Integrating New Headlines with Existing Dataset")
    print("=" * 60)
    
    all_datasets = []
    
    # 1. Load original dataset (data/scraped_headlines_data.csv) - this remains unchanged
    if os.path.exists(original_dataset_path):
        try:
            original_df = pd.read_csv(original_dataset_path)
            print(f"\n[1] Loaded original dataset: {len(original_df)} headlines")
            print(f"    File: {original_dataset_path} (this file will NOT be modified)")
            
            # Ensure it has required columns
            if 'headline' in original_df.columns and 'source' in original_df.columns:
                # Add collection_date if missing
                if 'collection_date' not in original_df.columns:
                    original_df['collection_date'] = 'initial'
                
                # Keep only required columns
                original_df = original_df[['headline', 'source', 'collection_date']]
                all_datasets.append(original_df)
            else:
                print(f"  Warning: Original dataset missing required columns. Skipping.")
        except Exception as e:
            print(f"  Warning: Could not load original dataset: {str(e)}")
    else:
        print(f"\n[1] Original dataset not found: {original_dataset_path}")
        print(f"    Note: If this is your first run, create this file with your original headlines.")
    
    # 2. Load existing integrated dataset (data/daily_updated_headlines_data.csv) if it exists
    # This file already contains original + previous daily collections
    if os.path.exists(integrated_dataset_path):
        try:
            existing_df = pd.read_csv(integrated_dataset_path)
            print(f"[2] Loaded existing integrated dataset: {len(existing_df)} headlines")
            print(f"    File: {integrated_dataset_path}")
            
            # Ensure it has required columns
            if 'headline' in existing_df.columns and 'source' in existing_df.columns:
                # Add collection_date if missing
                if 'collection_date' not in existing_df.columns:
                    existing_df['collection_date'] = 'unknown'
                
                # Keep only required columns
                existing_df = existing_df[['headline', 'source', 'collection_date']]
                all_datasets.append(existing_df)
            else:
                print(f"  Warning: Integrated dataset missing required columns. Skipping.")
        except Exception as e:
            print(f"  Warning: Could not load integrated dataset: {str(e)}")
    else:
        print(f"[2] Integrated dataset not found: {integrated_dataset_path}")
        print(f"    Will be created with original + new daily headlines")
    
    # 3. Add new daily headlines
    print(f"\n[3] Adding {len(daily_headlines)} new daily headlines")
    if len(daily_headlines) > 0:
        print(f"    Sample new headlines:")
        for i, row in daily_headlines.head(3).iterrows():
            print(f"      - [{row['source']}] {row['headline'][:70]}{'...' if len(row['headline']) > 70 else ''}")
        if len(daily_headlines) > 3:
            print(f"      ... and {len(daily_headlines) - 3} more")
    all_datasets.append(daily_headlines)
    
    # 4. Combine all datasets
    if all_datasets:
        combined_df = pd.concat(all_datasets, ignore_index=True)
        print(f"\n[4] Combined dataset before deduplication: {len(combined_df)} headlines")
        
        # 5. Remove duplicates based on headline text (case-insensitive)
        # Normalize headlines for comparison
        combined_df['headline_normalized'] = combined_df['headline'].str.lower().str.strip()
        
        # Keep first occurrence of each unique headline
        combined_df = combined_df.drop_duplicates(subset=['headline_normalized'], keep='first')
        
        # Remove the normalization column
        combined_df = combined_df.drop(columns=['headline_normalized'])
        
        print(f"[5] After removing duplicates: {len(combined_df)} unique headlines")
        
        # 6. Save updated integrated dataset
        combined_df.to_csv(integrated_dataset_path, index=False)
        print(f"\n[6] Updated dataset saved to: {integrated_dataset_path}")
        print(f"    Note: {original_dataset_path} remains unchanged (original dataset preserved)")
        
        # 7. Display summary statistics
        print(f"\n" + "=" * 60)
        print("Final Dataset Statistics")
        print("=" * 60)
        print(f"   Total unique headlines: {len(combined_df)}")
        
        # Source distribution
        if 'source' in combined_df.columns:
            source_dist = combined_df['source'].value_counts()
            print(f"\n   By Source:")
            for source, count in source_dist.items():
                percentage = (count / len(combined_df)) * 100
                print(f"      {source}: {count} ({percentage:.1f}%)")
        
        # Collection date distribution
        if 'collection_date' in combined_df.columns:
            date_dist = combined_df['collection_date'].value_counts().head(10)
            print(f"\n   Top Collection Dates:")
            for date, count in date_dist.items():
                print(f"      {date}: {count} headlines")
        
        return combined_df
    else:
        # No existing datasets, just save the new one
        daily_headlines.to_csv(integrated_dataset_path, index=False)
        print(f"\nCreated new integrated dataset with {len(daily_headlines)} headlines")
        print(f"Saved to: {integrated_dataset_path}")
        return daily_headlines


def main():
    """Main function to run daily collection."""
    print(f"\nDaily Headline Collection - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # Collect daily headlines
        daily_headlines = collect_daily_headlines()
        
        # Integrate with existing dataset
        if len(daily_headlines) > 0:
            integrate_with_existing_dataset(daily_headlines)
        else:
            print("\nNo new headlines collected today.")
        
        print("\n" + "=" * 60)
        print("Daily collection complete!")
        print("=" * 60)
        return 0
        
    except Exception as e:
        print(f"\nError during collection: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
