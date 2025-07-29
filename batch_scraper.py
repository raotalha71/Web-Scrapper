import pandas as pd
import os
import json
import sys
import logging
import datetime
import time
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"scraper_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

class SmartScraper:
    """Smart scraper that adapts to website characteristics"""
    
    def __init__(self, csv_file='scraped_data.csv'):
        self.csv_file = csv_file
        self.setup_csv()
    
    def setup_csv(self):
        """Setup CSV structure if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            columns = [
                'id', 'session_id', 'url', 'final_url', 'domain', 'title', 'meta_description', 'meta_keywords',
                'h1_headings', 'h2_headings', 'h3_headings', 'content_text', 'word_count',
                'links_internal', 'links_external', 'images_count', 'forms_count', 'scripts_count',
                'page_size_kb', 'load_time_ms', 'status_code', 'content_type', 'language',
                'charset', 'canonical_url', 'og_title', 'og_description', 'og_image',
                'twitter_title', 'twitter_description', 'schema_org_data', 'social_links',
                'contact_info', 'breadcrumbs', 'page_depth', 'found_links_count', 
                'error_message', 'scraped_at', 'scraper_version', 'proxy_used', 'scraper_method'
            ]
            
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Created new CSV file: {self.csv_file}")
    
    def scrape_with_requests(self, url, special_handling=None):
        """Scrape using requests and BeautifulSoup"""
        logging.info(f"Scraping with requests_bs4: {url}")
        
        # Default headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # If enhanced headers are needed
        if special_handling and "enhanced" in special_handling.lower():
            headers.update({
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            })
        
        # Handle redirects if mentioned in special handling
        redirect_url = None
        if special_handling and "redirects to" in special_handling:
            import re
            redirect_match = re.search(r"redirects to (https?://[^\s;]+)", special_handling)
            if redirect_match:
                redirect_url = redirect_match.group(1)
                url = redirect_url
                logging.info(f"Using redirected URL: {url}")
        
        start_time = datetime.datetime.now()
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            end_time = datetime.datetime.now()
            load_time_ms = (end_time - start_time).total_seconds() * 1000
            
            if response.status_code >= 400:
                logging.error(f"Request failed with status code {response.status_code}")
                return None
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data
            data = self._extract_data_from_soup(soup, url, response, load_time_ms)
            data['scraper_method'] = 'requests_bs4'
            
            # Save to CSV
            self.save_to_csv(data)
            
            return data
            
        except Exception as e:
            logging.error(f"Error in requests scraping: {str(e)}")
            return None
    
    def scrape_with_playwright(self, url, special_handling=None):
        """Scrape using Playwright browser automation"""
        logging.info(f"Scraping with playwright: {url}")
        
        start_time = datetime.datetime.now()
        
        try:
            with sync_playwright() as p:
                # Configure browser with anti-bot measures
                browser_args = [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-blink-features=AutomationControlled'
                ]
                
                # Launch browser
                browser = p.chromium.launch(
                    headless=True,
                    args=browser_args
                )
                
                # Create context with specific settings
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    java_script_enabled=True,
                    ignore_https_errors=True
                )
                
                # Add script to evade bot detection
                context.add_init_script("""
                    // Remove webdriver traces
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    
                    // Override chrome property
                    window.chrome = {runtime: {}};
                    
                    // Override permissions
                    const originalQuery = window.navigator.permissions.query;
                    window.navigator.permissions.query = (parameters) => (
                        parameters.name === 'notifications' ?
                            Promise.resolve({ state: Notification.permission }) :
                            originalQuery(parameters)
                    );
                    
                    // Override plugins
                    Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                """)
                
                page = context.new_page()
                
                try:
                    # Navigate to the page
                    response = page.goto(
                        url,
                        timeout=30000,  # 30 seconds timeout
                        wait_until='networkidle'  # Wait for network to be quiet
                    )
                    
                    end_time = datetime.datetime.now()
                    load_time_ms = (end_time - start_time).total_seconds() * 1000
                    
                    if response and response.status >= 400:
                        logging.error(f"Page navigation failed with status {response.status}")
                        browser.close()
                        return None
                    
                    # Get page content
                    content = page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Extract data
                    data = {
                        'id': f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(url)) % 10000}",
                        'session_id': f"playwright_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        'url': url,
                        'final_url': page.url,
                        'domain': urlparse(url).netloc,
                        'title': page.title(),
                        'meta_description': page.evaluate('document.querySelector("meta[name=\'description\']")?.content || ""'),
                        'meta_keywords': page.evaluate('document.querySelector("meta[name=\'keywords\']")?.content || ""'),
                        'h1_headings': ' | '.join(page.evaluate('Array.from(document.querySelectorAll("h1")).map(el => el.textContent.trim())')),
                        'h2_headings': ' | '.join(page.evaluate('Array.from(document.querySelectorAll("h2")).map(el => el.textContent.trim())')),
                        'h3_headings': ' | '.join(page.evaluate('Array.from(document.querySelectorAll("h3")).map(el => el.textContent.trim())')),
                        'content_text': page.evaluate('document.body.textContent.trim()'),
                        'word_count': len(page.evaluate('document.body.textContent.trim()').split()),
                        'links_internal': page.evaluate(f'''
                            () => {{
                                const currentDomain = '{urlparse(url).netloc}';
                                const links = Array.from(document.querySelectorAll('a[href]'));
                                return links.filter(link => {{
                                    try {{
                                        const href = link.href;
                                        const linkDomain = new URL(href).hostname;
                                        return linkDomain === currentDomain || linkDomain === 'www.' + currentDomain || 'www.' + linkDomain === currentDomain;
                                    }} catch {{
                                        return false;
                                    }}
                                }}).length;
                            }}
                        '''),
                        'links_external': page.evaluate(f'''
                            () => {{
                                const currentDomain = '{urlparse(url).netloc}';
                                const links = Array.from(document.querySelectorAll('a[href]'));
                                return links.filter(link => {{
                                    try {{
                                        const href = link.href;
                                        if (!href.startsWith('http')) return false;
                                        const linkDomain = new URL(href).hostname;
                                        return linkDomain !== currentDomain && 'www.' + linkDomain !== currentDomain && linkDomain !== 'www.' + currentDomain;
                                    }} catch {{
                                        return false;
                                    }}
                                }}).length;
                            }}
                        '''),
                        'images_count': page.evaluate('document.querySelectorAll("img").length'),
                        'forms_count': page.evaluate('document.querySelectorAll("form").length'),
                        'scripts_count': page.evaluate('document.querySelectorAll("script").length'),
                        'page_size_kb': len(content) // 1024,
                        'load_time_ms': load_time_ms,
                        'status_code': response.status if response else 0,
                        'content_type': response.headers.get('content-type', '') if response else '',
                        'language': page.evaluate('document.documentElement.lang || ""'),
                        'charset': soup.original_encoding,
                        'canonical_url': page.evaluate('document.querySelector("link[rel=\'canonical\']")?.href || ""'),
                        'og_title': page.evaluate('document.querySelector("meta[property=\'og:title\']")?.content || ""'),
                        'og_description': page.evaluate('document.querySelector("meta[property=\'og:description\']")?.content || ""'),
                        'og_image': page.evaluate('document.querySelector("meta[property=\'og:image\']")?.content || ""'),
                        'twitter_title': page.evaluate('document.querySelector("meta[name=\'twitter:title\']")?.content || ""'),
                        'twitter_description': page.evaluate('document.querySelector("meta[name=\'twitter:description\']")?.content || ""'),
                        'schema_org_data': str(soup.find_all('script', type='application/ld+json'))[:1000],
                        'social_links': self._extract_social_links(soup),
                        'contact_info': self._extract_contact_info(soup),
                        'breadcrumbs': self._extract_breadcrumbs(soup),
                        'page_depth': 0,
                        'found_links_count': page.evaluate('document.querySelectorAll("a[href]").length'),
                        'error_message': '',
                        'scraped_at': datetime.datetime.now().isoformat(),
                        'scraper_version': '3.0.0',
                        'proxy_used': 'None',
                        'scraper_method': 'playwright'
                    }
                    
                    # Save to CSV
                    self.save_to_csv(data)
                    
                    browser.close()
                    return data
                    
                except Exception as e:
                    browser.close()
                    logging.error(f"Error during browser scraping: {str(e)}")
                    return None
                
        except Exception as e:
            logging.error(f"Error initializing browser: {str(e)}")
            return None
    
    def _extract_data_from_soup(self, soup, url, response, load_time_ms):
        """Extract structured data from BeautifulSoup object"""
        domain = urlparse(url).netloc
        
        # Extract all links
        links = soup.find_all('a', href=True)
        internal_links = 0
        external_links = 0
        
        for link in links:
            href = link.get('href', '')
            try:
                if href.startswith('/') or domain in href:
                    internal_links += 1
                elif href.startswith(('http://', 'https://')) and domain not in href:
                    external_links += 1
            except:
                pass
        
        # Create data dictionary
        data = {
            'id': f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{abs(hash(url)) % 10000}",
            'session_id': f"requests_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'url': url,
            'final_url': response.url,
            'domain': domain,
            'title': soup.title.text.strip() if soup.title else '',
            'meta_description': soup.find('meta', attrs={'name': 'description'}).get('content', '') if soup.find('meta', attrs={'name': 'description'}) else '',
            'meta_keywords': soup.find('meta', attrs={'name': 'keywords'}).get('content', '') if soup.find('meta', attrs={'name': 'keywords'}) else '',
            'h1_headings': ' | '.join([h.text.strip() for h in soup.find_all('h1')]),
            'h2_headings': ' | '.join([h.text.strip() for h in soup.find_all('h2')]),
            'h3_headings': ' | '.join([h.text.strip() for h in soup.find_all('h3')]),
            'content_text': ' '.join(soup.body.text.split()) if soup.body else '',
            'word_count': len(soup.text.split()) if soup else 0,
            'links_internal': internal_links,
            'links_external': external_links,
            'images_count': len(soup.find_all('img')),
            'forms_count': len(soup.find_all('form')),
            'scripts_count': len(soup.find_all('script')),
            'page_size_kb': len(response.content) // 1024,
            'load_time_ms': load_time_ms,
            'status_code': response.status_code,
            'content_type': response.headers.get('Content-Type', ''),
            'language': soup.html.get('lang', '') if soup.html else '',
            'charset': response.encoding,
            'canonical_url': soup.find('link', rel='canonical').get('href', '') if soup.find('link', rel='canonical') else '',
            'og_title': soup.find('meta', property='og:title').get('content', '') if soup.find('meta', property='og:title') else '',
            'og_description': soup.find('meta', property='og:description').get('content', '') if soup.find('meta', property='og:description') else '',
            'og_image': soup.find('meta', property='og:image').get('content', '') if soup.find('meta', property='og:image') else '',
            'twitter_title': soup.find('meta', attrs={'name': 'twitter:title'}).get('content', '') if soup.find('meta', attrs={'name': 'twitter:title'}) else '',
            'twitter_description': soup.find('meta', attrs={'name': 'twitter:description'}).get('content', '') if soup.find('meta', attrs={'name': 'twitter:description'}) else '',
            'schema_org_data': str(soup.find_all('script', type='application/ld+json'))[:1000],
            'social_links': self._extract_social_links(soup),
            'contact_info': self._extract_contact_info(soup),
            'breadcrumbs': self._extract_breadcrumbs(soup),
            'page_depth': 0,
            'found_links_count': len(links),
            'error_message': '',
            'scraped_at': datetime.datetime.now().isoformat(),
            'scraper_version': '3.0.0',
            'proxy_used': 'None'
        }
        
        return data
    
    def _extract_social_links(self, soup):
        """Extract social media links from the page"""
        social_domains = ['facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com', 'youtube.com']
        social_links = []
        
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').lower()
            if any(domain in href for domain in social_domains):
                social_links.append(a.get('href'))
        
        return ' | '.join(social_links[:5])  # Limit to 5 links
    
    def _extract_contact_info(self, soup):
        """Extract contact information from the page"""
        import re
        
        # Find emails
        emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', soup.text)
        
        # Find phone numbers
        phones = re.findall(r'[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}', soup.text)
        
        # Combine and return
        return f"Emails: {', '.join(emails[:3])} | Phones: {', '.join(phones[:3])}"
    
    def _extract_breadcrumbs(self, soup):
        """Extract breadcrumb navigation if present"""
        breadcrumbs = []
        
        # Look for common breadcrumb containers
        breadcrumb_elements = soup.find_all('nav', class_=lambda x: x and 'breadcrumb' in x.lower())
        if not breadcrumb_elements:
            breadcrumb_elements = soup.find_all(class_=lambda x: x and 'breadcrumb' in x.lower())
        
        if breadcrumb_elements:
            for element in breadcrumb_elements:
                links = element.find_all('a')
                breadcrumbs = ' > '.join([a.text.strip() for a in links])
        
        return breadcrumbs
    
    def save_to_csv(self, data):
        """Save scraped data to CSV file"""
        try:
            # Read existing CSV
            if os.path.exists(self.csv_file):
                df = pd.read_csv(self.csv_file)
            else:
                df = pd.DataFrame()
            
            # Append new row
            new_row = pd.DataFrame([data])
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save back to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Data saved to {self.csv_file}")
            
        except Exception as e:
            logging.error(f"Error saving to CSV: {str(e)}")

def scrape_from_report(report_file, output_csv=None, max_sites=None):
    """Scrape websites based on a previously generated site access report"""
    logging.info(f"Starting scraping from report: {report_file}")
    
    # Initialize scraper
    scraper = SmartScraper(output_csv or 'scraped_data.csv')
    
    try:
        # Read the report file
        df = pd.read_csv(report_file)
        logging.info(f"Loaded {len(df)} sites from report")
        
        # Filter for accessible sites
        accessible_sites = df[(df['request_access'] == 'Yes') | (df['browser_access'] == 'Yes')]
        logging.info(f"Found {len(accessible_sites)} accessible sites")
        
        if max_sites:
            accessible_sites = accessible_sites.head(max_sites)
            logging.info(f"Limited to first {max_sites} sites")
        
        # Track results
        results = {
            'total': len(accessible_sites),
            'success': 0,
            'failed': 0,
            'methods': {}
        }
        
        # Process each site
        for i, (_, site) in enumerate(accessible_sites.iterrows()):
            url = site['url']
            method = site['scrape_method']
            special_handling = site['special_handling']
            
            logging.info(f"Processing site {i+1}/{len(accessible_sites)}: {url}")
            logging.info(f"  Method: {method}, Special handling: {special_handling}")
            
            success = False
            
            # Choose scraping method based on recommendation
            if method == 'requests_bs4' or method == 'requests_bs4_enhanced':
                data = scraper.scrape_with_requests(url, special_handling)
                success = data is not None
            elif method == 'playwright':
                data = scraper.scrape_with_playwright(url, special_handling)
                success = data is not None
            elif method == 'requests_json':
                # Not implemented yet
                logging.warning(f"JSON scraping not implemented yet, falling back to requests_bs4")
                data = scraper.scrape_with_requests(url, special_handling)
                success = data is not None
            else:
                logging.warning(f"Unknown or unsupported method: {method}, skipping")
                success = False
            
            # Update results
            if success:
                results['success'] += 1
                results['methods'][method] = results['methods'].get(method, 0) + 1
                logging.info(f"  SUCCESS: Successfully scraped {url}")
            else:
                results['failed'] += 1
                logging.error(f"  FAILED: Failed to scrape {url}")
            
            # Add delay between requests
            if i < len(accessible_sites) - 1:
                delay = min(5, 1 + (i % 5))  # Progressive delay to avoid rate limiting
                logging.info(f"  Waiting {delay} seconds before next request...")
                time.sleep(delay)
        
        return results
        
    except Exception as e:
        logging.error(f"Error in scrape_from_report: {str(e)}")
        return None

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python batch_scraper.py <report_file.csv> [max_sites]")
        return
    
    report_file = sys.argv[1]
    max_sites = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    output_csv = 'scraped_data.csv'
    
    print("=" * 80)
    print("Batch Website Scraper")
    print("=" * 80)
    print(f"This tool will scrape websites listed in {report_file}")
    print(f"Results will be saved to {output_csv}")
    print("=" * 80)
    
    if max_sites:
        print(f"Limiting to first {max_sites} sites")
    
    print("\nStarting scraping...")
    start_time = time.time()
    
    # Run the scraper
    results = scrape_from_report(report_file, output_csv, max_sites)
    
    if results:
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print(f"Scraping completed in {elapsed_time:.1f} seconds")
        print(f"Total sites: {results['total']}")
        print(f"Successful: {results['success']}")
        print(f"Failed: {results['failed']}")
        print("\nMethods used:")
        for method, count in results['methods'].items():
            print(f"  - {method}: {count} sites")
        print(f"\nResults saved to {output_csv}")
    else:
        print("No results. Check the log file for errors.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
