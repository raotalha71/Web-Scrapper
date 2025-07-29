import pandas as pd
import os
import json
import sys
import logging
import datetime
import time
import random
import csv
import urllib.parse
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException
from playwright.sync_api import sync_playwright, Page

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"proxy_scraper_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Directory for storing screenshots
screenshot_dir = "screenshots"
if not os.path.exists(screenshot_dir):
    os.makedirs(screenshot_dir)

class ProxyScraper:
    """Multi-attempt scraper with proxy rotation for challenging websites"""
    
    def __init__(self, csv_file='proxy_scraped_data.csv', max_attempts=5):
        self.csv_file = csv_file
        self.max_attempts = max_attempts
        self.setup_csv()
        self.session_id = f"proxy_session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.scraper_version = "1.0.0"
        self.user_agents = self.load_user_agents()
        self.free_proxies = self.load_free_proxies()
        
    def load_user_agents(self):
        """Load a list of user agents"""
        default_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15"
        ]
        
        if os.path.exists("user_agents.txt"):
            try:
                with open("user_agents.txt", 'r') as f:
                    agents = [line.strip() for line in f if line.strip()]
                if agents:
                    return agents
            except Exception as e:
                logging.warning(f"Error loading user agents: {e}")
        
        return default_agents
    
    def load_free_proxies(self):
        """Load a list of free proxies - in a real scenario, you'd use a proper proxy provider"""
        # These are just examples - most free proxies won't work well
        # In a real scenario, use a paid proxy service
        return [
            # Format: "http://ip:port"
            # Empty list by default - we'll try without proxies first
        ]
    
    def setup_csv(self):
        """Setup CSV structure if it doesn't exist"""
        if not os.path.exists(self.csv_file):
            columns = [
                'id', 'session_id', 'url', 'final_url', 'domain', 'title', 'meta_description', 
                'content_summary', 'successful_method', 'attempt_number', 'proxy_used', 
                'status_code', 'load_time_ms', 'scraped_at', 'screenshot_path', 'error_message'
            ]
            
            logging.info(f"Created new CSV file: {self.csv_file}")
            df = pd.DataFrame(columns=columns)
            df.to_csv(self.csv_file, index=False)
    
    def get_domain(self, url):
        """Extract domain from URL"""
        try:
            parsed = urllib.parse.urlparse(url)
            domain = parsed.netloc
            if not domain and not url.startswith(('http://', 'https://')):
                # Try adding https:// and parsing again
                parsed = urllib.parse.urlparse(f"https://{url}")
                domain = parsed.netloc
            return domain
        except Exception:
            return url
    
    def clean_url(self, url):
        """Ensure URL has proper scheme"""
        if not url.startswith(('http://', 'https://')):
            return f"https://{url}"
        return url
    
    def save_data(self, url, data):
        """Save scraped data to CSV"""
        try:
            # Read existing CSV
            if os.path.exists(self.csv_file) and os.path.getsize(self.csv_file) > 0:
                df = pd.read_csv(self.csv_file)
            else:
                # If file doesn't exist or is empty, create with columns
                self.setup_csv()
                df = pd.read_csv(self.csv_file)
            
            # Create a record
            domain = self.get_domain(url)
            
            record_id = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
            
            new_row = pd.DataFrame([{
                'id': record_id,
                'session_id': self.session_id,
                'url': url,
                'final_url': data.get('final_url', ''),
                'domain': domain,
                'title': data.get('title', ''),
                'meta_description': data.get('meta_description', ''),
                'content_summary': data.get('content_summary', ''),
                'successful_method': data.get('successful_method', ''),
                'attempt_number': data.get('attempt_number', 0),
                'proxy_used': data.get('proxy_used', ''),
                'status_code': data.get('status_code', 0),
                'load_time_ms': data.get('load_time_ms', 0),
                'scraped_at': datetime.datetime.now().isoformat(),
                'screenshot_path': data.get('screenshot_path', ''),
                'error_message': data.get('error_message', '')
            }])
            
            # Append to DataFrame
            df = pd.concat([df, new_row], ignore_index=True)
            
            # Save to CSV
            df.to_csv(self.csv_file, index=False)
            logging.info(f"Data saved to {self.csv_file}")
            return True
        except Exception as e:
            logging.error(f"Error saving data: {e}")
            return False
    
    def method1_simple_requests(self, url, proxy=None, attempt=1):
        """Basic requests with minimal headers"""
        data = {
            'successful_method': 'simple_requests',
            'attempt_number': attempt,
            'proxy_used': proxy or 'none',
            'final_url': url
        }
        
        start_time = time.time()
        
        try:
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0'
            }
            
            proxies = None
            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies, 
                timeout=30,
                allow_redirects=True,
                verify=False  # Ignore SSL errors
            )
            
            data['status_code'] = response.status_code
            data['final_url'] = response.url
            
            if response.status_code >= 400:
                raise Exception(f"HTTP Error: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic data
            data['title'] = soup.title.text.strip() if soup.title else ''
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['meta_description'] = meta_desc.get('content', '')
            
            # Get content summary (first 1000 chars of cleaned text)
            all_text = soup.get_text(separator=' ', strip=True)
            data['content_summary'] = all_text[:1000] + '...' if len(all_text) > 1000 else all_text
            
            data['success'] = True
            
        except Exception as e:
            data['success'] = False
            data['error_message'] = str(e)
            logging.error(f"Error in simple_requests for {url}: {e}")
        
        # Calculate load time
        data['load_time_ms'] = int((time.time() - start_time) * 1000)
        
        return data
    
    def method2_enhanced_requests(self, url, proxy=None, attempt=1):
        """Enhanced requests with extended headers and cookies handling"""
        data = {
            'successful_method': 'enhanced_requests',
            'attempt_number': attempt,
            'proxy_used': proxy or 'none',
            'final_url': url
        }
        
        start_time = time.time()
        
        try:
            session = requests.Session()
            
            # First make a HEAD request to get cookies
            headers = {
                'User-Agent': random.choice(self.user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Cache-Control': 'max-age=0',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Pragma': 'no-cache'
            }
            
            proxies = None
            if proxy:
                proxies = {
                    'http': proxy,
                    'https': proxy
                }
            
            # Try HEAD request first to get cookies
            try:
                session.head(
                    url, 
                    headers=headers, 
                    proxies=proxies, 
                    timeout=10,
                    allow_redirects=True,
                    verify=False  # Ignore SSL errors
                )
            except Exception as e:
                logging.warning(f"HEAD request failed for {url}: {e}")
            
            # Add a referrer that makes sense
            domain = self.get_domain(url)
            if domain:
                headers['Referer'] = f"https://www.google.com/search?q={domain}"
            
            # Main GET request
            response = session.get(
                url, 
                headers=headers, 
                proxies=proxies, 
                timeout=30,
                allow_redirects=True,
                verify=False  # Ignore SSL errors
            )
            
            data['status_code'] = response.status_code
            data['final_url'] = response.url
            
            if response.status_code >= 400:
                raise Exception(f"HTTP Error: {response.status_code}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic data
            data['title'] = soup.title.text.strip() if soup.title else ''
            
            # Get meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['meta_description'] = meta_desc.get('content', '')
            
            # Get content summary (first 1000 chars of cleaned text)
            all_text = soup.get_text(separator=' ', strip=True)
            data['content_summary'] = all_text[:1000] + '...' if len(all_text) > 1000 else all_text
            
            data['success'] = True
            
        except Exception as e:
            data['success'] = False
            data['error_message'] = str(e)
            logging.error(f"Error in enhanced_requests for {url}: {e}")
        
        # Calculate load time
        data['load_time_ms'] = int((time.time() - start_time) * 1000)
        
        return data
    
    def method3_playwright_basic(self, url, proxy=None, attempt=1):
        """Basic Playwright automation"""
        data = {
            'successful_method': 'playwright_basic',
            'attempt_number': attempt,
            'proxy_used': proxy or 'none',
            'final_url': url,
            'screenshot_path': ''
        }
        
        start_time = time.time()
        
        try:
            with sync_playwright() as p:
                # Choose a browser (chromium, firefox, or webkit)
                browser = p.chromium.launch(headless=True)
                
                # Create a new browser context
                context = browser.new_context(
                    user_agent=random.choice(self.user_agents),
                )
                
                # Create a new page
                page = context.new_page()
                
                # Navigate to the URL
                response = page.goto(url, timeout=30000, wait_until='domcontentloaded')
                
                # Save status code
                data['status_code'] = response.status if response else 0
                data['final_url'] = page.url
                
                # Extract basic data
                data['title'] = page.title()
                
                # Get meta description
                data['meta_description'] = page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.getAttribute('content') : '';
                    }
                """)
                
                # Get content summary
                content = page.evaluate("""
                    () => {
                        return document.body ? document.body.innerText.replace(/\\s+/g, ' ').trim() : '';
                    }
                """)
                
                data['content_summary'] = content[:1000] + '...' if len(content) > 1000 else content
                
                # Take a screenshot
                screenshot_path = os.path.join(
                    screenshot_dir, 
                    f"{self.get_domain(url).replace('.', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                page.screenshot(path=screenshot_path)
                data['screenshot_path'] = screenshot_path
                
                # Close the browser
                browser.close()
                
                data['success'] = True
                
        except Exception as e:
            data['success'] = False
            data['error_message'] = str(e)
            logging.error(f"Error in playwright_basic for {url}: {e}")
        
        # Calculate load time
        data['load_time_ms'] = int((time.time() - start_time) * 1000)
        
        return data
    
    def method4_playwright_stealth(self, url, proxy=None, attempt=1):
        """Stealth Playwright with advanced evasion techniques"""
        data = {
            'successful_method': 'playwright_stealth',
            'attempt_number': attempt,
            'proxy_used': proxy or 'none',
            'final_url': url,
            'screenshot_path': ''
        }
        
        start_time = time.time()
        
        try:
            with sync_playwright() as p:
                browser_type = p.chromium
                
                # Launch options to appear more like a real browser
                browser = browser_type.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-extensions',
                        '--disable-component-extensions-with-background-pages',
                        '--disable-features=TranslateUI,BlinkGenPropertyTrees',
                        '--disable-ipc-flooding-protection',
                        '--enable-features=NetworkService,NetworkServiceInProcess',
                        '--force-color-profile=srgb',
                        '--disable-features=Translate',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-accelerated-2d-canvas',
                        '--no-first-run',
                        '--no-zygote',
                        '--disable-gpu'
                    ]
                )
                
                # Create a context with proxy if provided
                context_options = {
                    'viewport': {'width': 1920, 'height': 1080},
                    'user_agent': random.choice(self.user_agents),
                    'locale': 'en-US',
                    'timezone_id': 'America/New_York',
                    'has_touch': False,
                    'java_script_enabled': True,
                    'ignore_https_errors': True
                }
                
                if proxy:
                    context_options['proxy'] = {
                        'server': proxy
                    }
                
                context = browser.new_context(**context_options)
                
                # Add stealth script
                context.add_init_script("""
                    // Overwrite navigator.webdriver
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => false,
                    });
                    
                    // Overwrite plugins
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => {
                            return [{
                                0: {
                                    type: "application/pdf",
                                    suffixes: "pdf",
                                    description: "Portable Document Format"
                                },
                                name: "PDF Viewer",
                                filename: "internal-pdf-viewer",
                                description: "Portable Document Format",
                                length: 1
                            }];
                        },
                    });
                    
                    // Overwrite languages
                    Object.defineProperty(navigator, 'languages', {
                        get: () => ['en-US', 'en'],
                    });
                """)
                
                page = context.new_page()
                
                # Set extra headers to appear more like a real browser
                page.set_extra_http_headers({
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Cache-Control': 'max-age=0',
                    'Sec-Ch-Ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'Upgrade-Insecure-Requests': '1'
                })
                
                # Random mouse movements before navigation
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                
                # Visit the site
                response = page.goto(url, wait_until='domcontentloaded', timeout=45000)
                page.wait_for_timeout(random.randint(2000, 4000))  # Wait for any additional scripts to load
                
                # More human-like behavior
                page.mouse.move(random.randint(100, 500), random.randint(100, 500))
                page.wait_for_timeout(random.randint(500, 1500))
                
                # Random scroll behavior
                page.evaluate("""
                    () => {
                        window.scrollTo(0, Math.floor(Math.random() * 200));
                        setTimeout(() => {
                            window.scrollTo(0, Math.floor(Math.random() * 500));
                        }, Math.floor(Math.random() * 1000));
                    }
                """)
                
                page.wait_for_timeout(random.randint(1000, 3000))
                
                # Get information
                data['status_code'] = response.status if response else 0
                data['final_url'] = page.url
                data['title'] = page.title()
                
                # Get meta description
                data['meta_description'] = page.evaluate("""
                    () => {
                        const meta = document.querySelector('meta[name="description"]');
                        return meta ? meta.getAttribute('content') : '';
                    }
                """)
                
                # Get content summary
                content = page.evaluate("""
                    () => {
                        return document.body ? document.body.innerText.replace(/\\s+/g, ' ').trim() : '';
                    }
                """)
                
                data['content_summary'] = content[:1000] + '...' if content and len(content) > 1000 else (content or '')
                
                # Take a screenshot
                screenshot_path = os.path.join(
                    screenshot_dir, 
                    f"{self.get_domain(url).replace('.', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                )
                page.screenshot(path=screenshot_path)
                data['screenshot_path'] = screenshot_path
                
                # Close browser
                browser.close()
                
                data['success'] = True
                
        except Exception as e:
            data['success'] = False
            data['error_message'] = str(e)
            logging.error(f"Error in playwright_stealth for {url}: {e}")
        
        # Calculate load time
        data['load_time_ms'] = int((time.time() - start_time) * 1000)
        
        return data
    
    def method5_domain_verification(self, url, attempt=1):
        """Verify if domain exists or has changed"""
        data = {
            'successful_method': 'domain_verification',
            'attempt_number': attempt,
            'proxy_used': 'none',
            'final_url': url
        }
        
        domain = self.get_domain(url)
        start_time = time.time()
        
        try:
            # Try to find alternative domain formats
            alt_domains = [
                f"https://{domain}",
                f"http://{domain}",
                f"https://www.{domain.replace('www.', '')}",
                f"http://www.{domain.replace('www.', '')}"
            ]
            
            if '.' in domain:
                base_name = domain.split('.')[0]
                alt_domains.extend([
                    f"https://{base_name}.com",
                    f"https://www.{base_name}.com",
                    f"https://{base_name}.net",
                    f"https://www.{base_name}.net",
                    f"https://{base_name}.org",
                    f"https://www.{base_name}.org"
                ])
            
            for alt_url in alt_domains:
                try:
                    response = requests.head(
                        alt_url,
                        headers={'User-Agent': random.choice(self.user_agents)},
                        timeout=10,
                        allow_redirects=True
                    )
                    
                    if response.status_code < 400:
                        logging.info(f"Found alternative URL: {alt_url} for {url}")
                        data['final_url'] = alt_url
                        data['success'] = True
                        data['content_summary'] = f"Domain verification found alternative URL: {alt_url}"
                        return data
                except Exception:
                    continue
            
            data['success'] = False
            data['error_message'] = "Domain verification failed to find alternative URLs"
            
        except Exception as e:
            data['success'] = False
            data['error_message'] = str(e)
            logging.error(f"Error in domain_verification for {url}: {e}")
        
        # Calculate load time
        data['load_time_ms'] = int((time.time() - start_time) * 1000)
        
        return data
    
    def scrape_url_with_multiple_attempts(self, url):
        """Try multiple methods with increasing complexity until one succeeds"""
        url = self.clean_url(url)
        logging.info(f"Starting multi-attempt scraping for: {url}")
        
        # Method 1: Simple requests
        logging.info(f"Attempt 1: Simple requests for {url}")
        result = self.method1_simple_requests(url, attempt=1)
        if result.get('success'):
            logging.info(f"SUCCESS: Simple requests method worked for {url}")
            self.save_data(url, result)
            return result
        
        time.sleep(random.randint(1, 3))
        
        # Method 2: Enhanced requests
        logging.info(f"Attempt 2: Enhanced requests for {url}")
        result = self.method2_enhanced_requests(url, attempt=2)
        if result.get('success'):
            logging.info(f"SUCCESS: Enhanced requests method worked for {url}")
            self.save_data(url, result)
            return result
        
        time.sleep(random.randint(2, 4))
        
        # Method 3: Basic Playwright
        logging.info(f"Attempt 3: Basic Playwright for {url}")
        result = self.method3_playwright_basic(url, attempt=3)
        if result.get('success'):
            logging.info(f"SUCCESS: Basic Playwright method worked for {url}")
            self.save_data(url, result)
            return result
        
        time.sleep(random.randint(2, 5))
        
        # Method 4: Stealth Playwright
        logging.info(f"Attempt 4: Stealth Playwright for {url}")
        result = self.method4_playwright_stealth(url, attempt=4)
        if result.get('success'):
            logging.info(f"SUCCESS: Stealth Playwright method worked for {url}")
            self.save_data(url, result)
            return result
        
        time.sleep(random.randint(2, 5))
        
        # Method 5: Domain verification (check for alternative URLs)
        logging.info(f"Attempt 5: Domain verification for {url}")
        result = self.method5_domain_verification(url, attempt=5)
        if result.get('success'):
            logging.info(f"SUCCESS: Domain verification found alternative URL for {url}: {result.get('final_url')}")
            self.save_data(url, result)
            # Now try scraping the alternative URL
            alt_url = result.get('final_url')
            logging.info(f"Attempting to scrape alternative URL: {alt_url}")
            alt_result = self.method4_playwright_stealth(alt_url, attempt=5)
            if alt_result.get('success'):
                logging.info(f"SUCCESS: Scraping alternative URL worked: {alt_url}")
                alt_result['successful_method'] = 'domain_verification+playwright_stealth'
                self.save_data(url, alt_result)
                return alt_result
            return result
            
        # All methods failed
        logging.error(f"FAILED: All methods failed for {url}")
        result['successful_method'] = 'none'
        self.save_data(url, result)
        return result

def process_challenging_sites(report_file, output_csv=None, max_sites=None):
    """Process sites that were marked as challenging in the site access report"""
    if not os.path.exists(report_file):
        logging.error(f"Report file not found: {report_file}")
        return None
    
    logging.info(f"Starting proxy scraping from report: {report_file}")
    
    # Create the scraper
    scraper = ProxyScraper(csv_file=output_csv or 'proxy_scraped_data.csv')
    
    # Read the report file
    try:
        sites = []
        with open(report_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Only include sites that were not accessible with standard methods
                if (row.get('request_access', 'No') == 'No' or 
                    row.get('scrape_method', '') in ['needs_investigation', 'advanced_techniques']):
                    sites.append({
                        'url': row.get('url', ''),
                        'method': row.get('scrape_method', 'advanced_techniques'),
                        'special_handling': row.get('special_handling', '')
                    })
    except Exception as e:
        logging.error(f"Error reading report file: {e}")
        return None
    
    logging.info(f"Loaded {len(sites)} challenging sites from report")
    
    # Limit the number of sites if requested
    if max_sites and max_sites < len(sites):
        logging.info(f"Limiting to first {max_sites} sites")
        sites = sites[:max_sites]
    
    # Initialize counters
    results = {
        'total': len(sites),
        'success': 0,
        'failed': 0,
        'methods': {}
    }
    
    # Process each site
    for i, site in enumerate(sites):
        url = site['url']
        
        logging.info(f"Processing site {i+1}/{len(sites)}: {url}")
        logging.info(f"  Method: multi-attempt, Special handling: {site['special_handling']}")
        
        # Attempt to scrape with multiple methods
        result = scraper.scrape_url_with_multiple_attempts(url)
        
        # Update counters
        if result.get('success', False):
            results['success'] += 1
            method = result.get('successful_method', 'unknown')
            results['methods'][method] = results['methods'].get(method, 0) + 1
            logging.info(f"  SUCCESS: Successfully scraped {url} with method {method}")
        else:
            results['failed'] += 1
            logging.error(f"  FAILED: Failed to scrape {url}")
        
        # Add delay between requests (more significant for challenging sites)
        if i < len(sites) - 1:
            delay = random.randint(5, 10)  # Random delay between 5-10 seconds
            logging.info(f"  Waiting {delay} seconds before next request...")
            time.sleep(delay)
    
    return results

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python proxy_scraper.py <report_file.csv> [max_sites]")
        return
    
    report_file = sys.argv[1]
    max_sites = int(sys.argv[2]) if len(sys.argv) > 2 else None
    
    output_csv = 'proxy_scraped_data.csv'
    
    print("=" * 80)
    print("Multi-Method Proxy Website Scraper")
    print("=" * 80)
    print(f"This tool will attempt to scrape challenging websites listed in {report_file}")
    print(f"Results will be saved to {output_csv}")
    print("=" * 80)
    
    if max_sites:
        print(f"Limiting to first {max_sites} sites")
    
    print("\nStarting proxy scraping...")
    start_time = time.time()
    
    # Run the scraper
    results = process_challenging_sites(report_file, output_csv, max_sites)
    
    if results:
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print(f"Proxy scraping completed in {elapsed_time:.1f} seconds")
        print(f"Total sites: {results['total']}")
        print(f"Successful: {results['success']}")
        print(f"Failed: {results['failed']}")
        print("\nMethods used:")
        for method, count in results['methods'].items():
            print(f"  - {method}: {count} sites")
        print(f"\nResults saved to {output_csv}")
        print(f"Screenshots saved to {screenshot_dir}")
    else:
        print("No results. Check the log file for errors.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
