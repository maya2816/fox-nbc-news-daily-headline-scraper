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
import random
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


def scrape_headlines_nbcnews_latest(url="https://www.nbcnews.com/latest-stories/", max_retries=3, delay=1, verbose=True, use_selenium=True, max_load_more_clicks=5):
    """
    Scrape headline titles from NBC News Latest Stories page.
    This page has a cleaner, more organized structure with better headline coverage.
    Uses Selenium to click "LOAD MORE" button to retrieve additional headlines.
    
    Args:
        url: NBC News Latest Stories URL (default: https://www.nbcnews.com/latest-stories/)
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Delay between retries in seconds (default: 1)
        verbose: Print scraped headlines (default: True)
        use_selenium: Whether to use Selenium to click "LOAD MORE" button (default: True)
        max_load_more_clicks: Maximum number of times to click "LOAD MORE" (default: 5)
    
    Returns:
        list: List of headline strings (titles only, no URLs)
    """
    headlines = []
    seen = set()  # Track unique headlines (case-insensitive)
    
    # Keywords to exclude (sponsored content, image credits, navigation, etc.)
    exclude_keywords = [
        'promotion', 'sponsored', 'advertisement', 'advert', 'commercial',
        'getty images', 'via ap', 'via reuters', 'via getty', 'photo by',
        'photographer', 'credit:', 'image credit', 'nbc news sitemap',
        'site map', 'closed captioning', 'load more'
    ]
    
    def is_valid_headline(text):
        """Check if text is a valid headline"""
        if not text or len(text) < 15 or len(text) > 200:
            return False
        text_lower = text.lower().strip()
        if ' ' not in text_lower:
            return False
        for keyword in exclude_keywords:
            if keyword in text_lower:
                return False
        return True
    
    def extract_headlines_from_html(html_content):
        """Extract headlines from HTML content"""
        soup = BeautifulSoup(html_content, "html.parser")
        extracted = []
        
        # Latest Stories page structure: headlines are in h2 tags with various classes
        headline_selectors = [
            'h2 a',  # Most common: h2 with link inside
            'h3 a',  # Some headlines use h3
            'article h2 a',  # Headlines within article tags
            'article h3 a',
            'h2.wide-tease-item__headline a',  # Specific Latest Stories structure
            'h2.styles_teaseTitle__ClSV0 a'  # Another specific structure
        ]
        
        for selector in headline_selectors:
            for element in soup.select(selector):
                headline_text = element.get_text(strip=True)
                if is_valid_headline(headline_text) and headline_text.lower() not in seen:
                    extracted.append(headline_text)
                    seen.add(headline_text.lower())
        
        # Also check for specific Latest Stories page structure
        story_containers = soup.find_all(['li', 'div'], class_=lambda x: x and ('story' in x.lower() or 'item' in x.lower() or 'article' in x.lower()))
        for container in story_containers:
            for tag in ['h2', 'h3', 'h4']:
                heading = container.find(tag)
                if heading:
                    link = heading.find('a')
                    if link:
                        headline_text = link.get_text(strip=True)
                        if is_valid_headline(headline_text) and headline_text.lower() not in seen:
                            extracted.append(headline_text)
                            seen.add(headline_text.lower())
        
        return extracted
    
    # Try Selenium first if requested and available
    if use_selenium:
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.common.exceptions import TimeoutException, NoSuchElementException
            
            # Try to use webdriver-manager for automatic ChromeDriver management
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                use_webdriver_manager = True
            except ImportError:
                use_webdriver_manager = False
            
            print("  Using Selenium to load additional headlines via 'LOAD MORE' button...")
            
            # Set up Chrome options for headless mode
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            driver = None
            try:
                if use_webdriver_manager:
                    service = Service(ChromeDriverManager().install())
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                else:
                    # Fallback: try to find chromedriver in PATH
                    driver = webdriver.Chrome(options=chrome_options)
                driver.set_page_load_timeout(30)
                driver.get(url)
                
                # Wait for page to load
                time.sleep(3)
                
                # Extract initial headlines
                initial_headlines = extract_headlines_from_html(driver.page_source)
                headlines.extend(initial_headlines)
                print(f"  Initial load: {len(initial_headlines)} headlines")
                
                # Click "LOAD MORE" button multiple times
                for click_num in range(max_load_more_clicks):
                    try:
                        # Try multiple selectors for the "LOAD MORE" button
                        load_more_selectors = [
                            "button:contains('Load More')",
                            "button:contains('LOAD MORE')",
                            "a:contains('Load More')",
                            "a:contains('LOAD MORE')",
                            "[data-testid*='load']",
                            "[class*='load']",
                            "[class*='Load']"
                        ]
                        
                        load_more_button = None
                        for selector in load_more_selectors:
                            try:
                                if selector.startswith("button:") or selector.startswith("a:"):
                                    # XPath for text contains
                                    text = selector.split("'")[1]
                                    xpath = f"//button[contains(text(), '{text}')] | //a[contains(text(), '{text}')]"
                                    load_more_button = driver.find_element(By.XPATH, xpath)
                                    break
                                else:
                                    load_more_button = driver.find_element(By.CSS_SELECTOR, selector)
                                    break
                            except NoSuchElementException:
                                continue
                        
                        if load_more_button is None:
                            # Try finding by visible text
                            try:
                                load_more_button = driver.find_element(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'load more')]")
                            except NoSuchElementException:
                                break
                        
                        # Check if button is visible and clickable
                        if load_more_button.is_displayed() and load_more_button.is_enabled():
                            # Scroll to button
                            driver.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                            time.sleep(1)
                            
                            # Click the button
                            driver.execute_script("arguments[0].click();", load_more_button)
                            print(f"  Clicked 'LOAD MORE' button (click {click_num + 1}/{max_load_more_clicks})")
                            
                            # Wait for new content to load
                            time.sleep(3)
                            
                            # Extract new headlines
                            new_headlines = extract_headlines_from_html(driver.page_source)
                            new_count = len(new_headlines) - len(headlines)
                            if new_count > 0:
                                headlines.extend(new_headlines[len(headlines):])
                                print(f"  Loaded {new_count} additional headlines (total: {len(headlines)})")
                            else:
                                print(f"  No new headlines loaded, stopping")
                                break
                        else:
                            print(f"  'LOAD MORE' button not clickable, stopping")
                            break
                            
                    except (NoSuchElementException, TimeoutException) as e:
                        print(f"  'LOAD MORE' button not found or not clickable after {click_num + 1} clicks")
                        break
                    except Exception as e:
                        print(f"  Error clicking 'LOAD MORE': {str(e)[:50]}")
                        break
                
            finally:
                if driver:
                    driver.quit()
            
            unique_headlines = list(headlines)
            print(f"  Successfully scraped {len(unique_headlines)} unique headlines from NBC Latest Stories (with Selenium)")
            
            if verbose and unique_headlines:
                print(f"\n  Sample headlines from NBC Latest Stories (showing first 5):")
                for i, headline in enumerate(unique_headlines[:5], 1):
                    print(f"    {i}. {headline[:80]}{'...' if len(headline) > 80 else ''}")
                if len(unique_headlines) > 5:
                    print(f"    ... and {len(unique_headlines) - 5} more")
            
            return unique_headlines
            
        except ImportError:
            print("  Selenium not available, falling back to requests/BeautifulSoup...")
            use_selenium = False
        except Exception as e:
            print(f"  Selenium error: {str(e)[:100]}, falling back to requests/BeautifulSoup...")
            use_selenium = False
    
    # Fallback to requests/BeautifulSoup if Selenium is not available or failed
    if not use_selenium:
        for attempt in range(max_retries):
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(url, timeout=15, headers=headers)
                
                if response.status_code != 200:
                    if attempt < max_retries - 1:
                        print(f"  Warning: Failed to fetch NBC Latest Stories (status {response.status_code}). Retrying...")
                        time.sleep(delay)
                        continue
                    else:
                        print(f"  Error: Failed to fetch NBC Latest Stories after {max_retries} attempts (status {response.status_code})")
                        return []
                
                extracted = extract_headlines_from_html(response.text)
                headlines.extend(extracted)
                
                unique_headlines = list(headlines)
                print(f"  Successfully scraped {len(unique_headlines)} unique headlines from NBC Latest Stories (without Selenium - limited to initial page)")
                
                if verbose and unique_headlines:
                    print(f"\n  Sample headlines from NBC Latest Stories (showing first 5):")
                    for i, headline in enumerate(unique_headlines[:5], 1):
                        print(f"    {i}. {headline[:80]}{'...' if len(headline) > 80 else ''}")
                    if len(unique_headlines) > 5:
                        print(f"    ... and {len(unique_headlines) - 5} more")
                
                return unique_headlines
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries} for NBC Latest Stories...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"  Error: Failed to fetch NBC Latest Stories after {max_retries} attempts: {str(e)}")
                    return []
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"  Retry {attempt + 1}/{max_retries} for NBC Latest Stories...")
                    time.sleep(delay)
                    continue
                else:
                    print(f"  Error: Unexpected error scraping NBC Latest Stories: {str(e)}")
                    return []
    
    return headlines if headlines else []


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
    Implements balanced sampling: scrapes both sources, finds the minimum count,
    and randomly samples that amount from the larger source to ensure equal class distribution.
    
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
    
    # Step 1: Scrape both homepages
    print("\n[1/2] Scraping Fox News homepage...")
    fox_headlines = scrape_headlines_foxnews()
    print(f"  Scraped {len(fox_headlines)} headlines from Fox News")
    
    # Small delay between requests
    time.sleep(2)
    
    print("\n[2/2] Scraping NBC News homepage...")
    nbc_headlines = scrape_headlines_nbcnews()
    print(f"  Scraped {len(nbc_headlines)} headlines from NBC News")
    
    # Step 2: Find minimum number of headlines
    min_headlines = min(len(fox_headlines), len(nbc_headlines))
    
    print(f"\n" + "=" * 60)
    print("Balancing Headlines")
    print("=" * 60)
    print(f"  Fox News scraped: {len(fox_headlines)} headlines")
    print(f"  NBC News scraped: {len(nbc_headlines)} headlines")
    print(f"  Minimum (min_headlines): {min_headlines} headlines")
    
    # Step 3: Randomly sample min_headlines from each source
    collected_headlines = []
    collected_sources = []
    collection_dates = []
    
    if min_headlines == 0:
        print("\n⚠️  Warning: No headlines were scraped from at least one source.")
        print("  Cannot create balanced dataset.")
        return pd.DataFrame(columns=['headline', 'source', 'collection_date'])
    
    # Sample from Fox News
    if len(fox_headlines) > min_headlines:
        fox_sampled = random.sample(fox_headlines, min_headlines)
        print(f"  Randomly sampled {min_headlines} headlines from Fox News (from {len(fox_headlines)} total)")
    else:
        fox_sampled = fox_headlines
        print(f"  Using all {len(fox_headlines)} headlines from Fox News")
    
    # Sample from NBC News
    if len(nbc_headlines) > min_headlines:
        nbc_sampled = random.sample(nbc_headlines, min_headlines)
        print(f"  Randomly sampled {min_headlines} headlines from NBC News (from {len(nbc_headlines)} total)")
    else:
        nbc_sampled = nbc_headlines
        print(f"  Using all {len(nbc_headlines)} headlines from NBC News")
    
    # Add Fox News headlines
    for headline in fox_sampled:
        collected_headlines.append(headline)
        collected_sources.append('FoxNews')
        collection_dates.append(target_date.strftime('%Y-%m-%d'))
    
    # Add NBC News headlines
    for headline in nbc_sampled:
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
        print(f"   ✓ Balanced: {len(new_df[new_df['source'] == 'FoxNews'])} == {len(new_df[new_df['source'] == 'NBC'])}")
        
        return new_df
    else:
        print("\nNo headlines were successfully collected.")
        return pd.DataFrame(columns=['headline', 'source', 'collection_date'])


def update_scraping_report(daily_headlines, existing_df_before, combined_df_after, 
                           report_path=None):
    """
    Update scraping report with statistics from the current scraping session.
    
    Args:
        daily_headlines: DataFrame with newly scraped headlines
        existing_df_before: DataFrame of existing dataset before adding new headlines (None if first run)
        combined_df_after: DataFrame after deduplication (final dataset)
        report_path: Path to report file (default: data/scraping_report.csv)
    
    Returns:
        DataFrame: Updated report
    """
    if report_path is None:
        report_path = os.path.join(DATA_DIR, 'scraping_report.csv')
    
    # Calculate statistics
    collection_date = datetime.now().strftime('%Y-%m-%d')
    total_scraped = len(daily_headlines)
    
    # Count by source
    fox_count = len(daily_headlines[daily_headlines['source'] == 'FoxNews'])
    nbc_count = len(daily_headlines[daily_headlines['source'] == 'NBC'])
    
    # Calculate how many were added vs duplicates
    if existing_df_before is not None:
        # Normalize existing headlines for comparison
        existing_normalized = set(existing_df_before['headline'].str.lower().str.strip())
        daily_normalized = set(daily_headlines['headline'].str.lower().str.strip())
        
        # Headlines that are new (not in existing dataset)
        new_headlines = daily_normalized - existing_normalized
        headlines_added = len(new_headlines)
        duplicates_found = total_scraped - headlines_added
        
        dataset_size_before = len(existing_df_before)
    else:
        # First run - all headlines are new
        headlines_added = total_scraped
        duplicates_found = 0
        dataset_size_before = 0
    
    dataset_size_after = len(combined_df_after) if combined_df_after is not None else headlines_added
    
    # Create report entry
    report_entry = pd.DataFrame({
        'scraping_date': [collection_date],
        'total_headlines_scraped': [total_scraped],
        'fox_news_count': [fox_count],
        'nbc_news_count': [nbc_count],
        'headlines_added': [headlines_added],
        'duplicates_skipped': [duplicates_found],
        'dataset_size_before': [dataset_size_before],
        'dataset_size_after': [dataset_size_after]
    })
    
    # Load existing report or create new
    if os.path.exists(report_path):
        try:
            existing_report = pd.read_csv(report_path)
            # Append new entry
            updated_report = pd.concat([existing_report, report_entry], ignore_index=True)
        except Exception as e:
            print(f"  Warning: Could not load existing report: {str(e)}")
            updated_report = report_entry
    else:
        updated_report = report_entry
    
    # Save updated report
    updated_report.to_csv(report_path, index=False)
    print(f"\n[7] Scraping report updated: {report_path}")
    print(f"    Date: {collection_date}")
    print(f"    Scraped: {total_scraped} (Fox: {fox_count}, NBC: {nbc_count})")
    print(f"    Added: {headlines_added}, Duplicates: {duplicates_found}")
    
    return updated_report


def integrate_with_existing_dataset(daily_headlines,
                                    original_dataset_path=None, 
                                    integrated_dataset_path=None):
    """
    Integrate collected headlines with existing dataset.
    - Loads original dataset (data/scraped_headlines_data.csv)  remains unchanged
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
    existing_combined_df = None  # For tracking what existed before adding new headlines
    
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
    
    # Create combined existing dataset (before adding new headlines) for report tracking
    if all_datasets:
        existing_combined_df = pd.concat(all_datasets, ignore_index=True)
        # Remove duplicates to get the actual existing dataset size
        existing_combined_df['headline_normalized'] = existing_combined_df['headline'].str.lower().str.strip()
        existing_combined_df = existing_combined_df.drop_duplicates(subset=['headline_normalized'], keep='first')
        existing_combined_df = existing_combined_df.drop(columns=['headline_normalized'])
    
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
        combined_df_before = pd.concat(all_datasets, ignore_index=True)
        print(f"\n[4] Combined dataset before deduplication: {len(combined_df_before)} headlines")
        
        # 5. Remove duplicates based on headline text (case-insensitive)
        # Normalize headlines for comparison
        combined_df_before['headline_normalized'] = combined_df_before['headline'].str.lower().str.strip()
        
        # Keep first occurrence of each unique headline
        combined_df_after = combined_df_before.drop_duplicates(subset=['headline_normalized'], keep='first')
        
        # Remove the normalization column
        combined_df_after = combined_df_after.drop(columns=['headline_normalized'])
        
        print(f"[5] After removing duplicates: {len(combined_df_after)} unique headlines")
        
        # 6. Save updated integrated dataset
        combined_df_after.to_csv(integrated_dataset_path, index=False)
        print(f"\n[6] Updated dataset saved to: {integrated_dataset_path}")
        print(f"    Note: {original_dataset_path} remains unchanged (original dataset preserved)")
        
        # 7. Update scraping report
        # Use existing_combined_df (original + previous integrated, before adding new headlines) for comparison
        update_scraping_report(daily_headlines, existing_combined_df, combined_df_after)
        
        # 8. Display summary statistics
        print(f"\n" + "=" * 60)
        print("Final Dataset Statistics")
        print("=" * 60)
        print(f"   Total unique headlines: {len(combined_df_after)}")
        
        # Source distribution
        if 'source' in combined_df_after.columns:
            source_dist = combined_df_after['source'].value_counts()
            print(f"\n   By Source:")
            for source, count in source_dist.items():
                percentage = (count / len(combined_df_after)) * 100
                print(f"      {source}: {count} ({percentage:.1f}%)")
        
        # Collection date distribution
        if 'collection_date' in combined_df_after.columns:
            date_dist = combined_df_after['collection_date'].value_counts().head(10)
            print(f"\n   Top Collection Dates:")
            for date, count in date_dist.items():
                print(f"      {date}: {count} headlines")
        
        return combined_df_after
    else:
        # No existing datasets, just save the new one
        daily_headlines.to_csv(integrated_dataset_path, index=False)
        print(f"\nCreated new integrated dataset with {len(daily_headlines)} headlines")
        print(f"Saved to: {integrated_dataset_path}")
        
        # Update scraping report (all headlines are new in this case - first run)
        update_scraping_report(daily_headlines, None, daily_headlines)
        
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
