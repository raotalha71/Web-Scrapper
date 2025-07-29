import requests
import json
import os
import time
import random
import datetime
import logging
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Configure logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"site_access_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def create_csv_report(results):
    """Create a CSV report of the test results"""
    import csv
    
    csv_file = os.path.join(log_dir, f"site_access_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'url', 'status', 'request_access', 'request_status_code', 
            'browser_access', 'bot_detection', 'load_time_ms', 'page_size_kb',
            'title', 'redirect_url', 'scrape_method', 'special_handling'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for site in results:
            writer.writerow(site)
    
    logging.info(f"CSV report created: {csv_file}")
    return csv_file

def test_with_requests(url):
    """Test site access using requests library"""
    start_time = time.time()
    
    # Custom headers to appear more like a normal browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.google.com/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'cross-site',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        result = {
            'success': response.status_code < 400,
            'status_code': response.status_code,
            'load_time_ms': int(elapsed_time),
            'page_size_kb': len(response.content) // 1024,
            'redirect_url': response.url,
            'content_type': response.headers.get('Content-Type', ''),
            'headers': dict(response.headers),
            'response_size': len(response.content)
        }
        
        # Try to get title with BeautifulSoup
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            result['title'] = soup.title.text.strip() if soup.title else 'No title'
        except:
            result['title'] = 'Could not parse title'
        
        return result
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

def test_with_playwright(url):
    """Test site access using Playwright browser automation"""
    start_time = time.time()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            # Add script to evade bot detection
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            """)
            
            page = context.new_page()
            
            try:
                response = page.goto(url, timeout=30000, wait_until='domcontentloaded')
                elapsed_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                # Check for bot detection
                content = page.content().lower()
                blocked_indicators = [
                    'please wait while your request is being verified',
                    'cloudflare',
                    'captcha',
                    'robot check',
                    'are you a robot',
                    'automated requests',
                    'bot detection',
                    'access denied',
                    'blocked'
                ]
                
                bot_detected = any(indicator in content for indicator in blocked_indicators)
                
                result = {
                    'success': response.status < 400 and not bot_detected,
                    'status_code': response.status,
                    'load_time_ms': int(elapsed_time),
                    'title': page.title(),
                    'final_url': page.url,
                    'bot_detected': bot_detected,
                    'content_size': len(content)
                }
                
                browser.close()
                return result
                
            except Exception as e:
                browser.close()
                return {
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }

def recommend_scrape_method(request_result, browser_result):
    """Recommend the best method to scrape a site based on test results"""
    
    # Default to using requests with BeautifulSoup as it's simpler
    method = "requests_bs4"
    special_handling = []
    
    # If requests failed but browser worked
    if not request_result.get('success') and browser_result.get('success'):
        method = "playwright"
        special_handling.append("Site requires JavaScript")
    
    # If both failed
    if not request_result.get('success') and not browser_result.get('success'):
        method = "needs_investigation"
        special_handling.append("Both methods failed")
    
    # If browser detected as bot
    if browser_result.get('bot_detected'):
        if request_result.get('success'):
            method = "requests_bs4_enhanced"
            special_handling.append("Bot detection present - use enhanced headers")
        else:
            method = "advanced_techniques"
            special_handling.append("Strong bot protection - may need proxies or special techniques")
    
    # Check for redirects
    if request_result.get('redirect_url') != request_result.get('original_url', ''):
        special_handling.append(f"Site redirects to {request_result.get('redirect_url')}")
    
    # Check for rate limiting headers
    rate_limit_headers = ['x-ratelimit-limit', 'x-ratelimit-remaining', 'retry-after']
    if any(h.lower() in request_result.get('headers', {}) for h in rate_limit_headers):
        special_handling.append("Rate limiting detected - implement delays")
    
    # Check for content type
    content_type = request_result.get('content_type', '').lower()
    if 'javascript' in content_type or 'json' in content_type:
        if method == "requests_bs4":
            method = "requests_json"
        special_handling.append("Site returns JSON/JavaScript - parse accordingly")
    
    return {
        "recommended_method": method,
        "special_handling": special_handling
    }

def test_site(url):
    """Comprehensive test of a single site"""
    logging.info(f"Testing site: {url}")
    
    # Test with requests
    logging.info(f"  Testing with requests...")
    request_result = test_with_requests(url)
    request_result['original_url'] = url
    
    request_success = request_result.get('success', False)
    logging.info(f"  Requests result: {'SUCCESS' if request_success else 'FAILED'}")
    if request_success:
        logging.info(f"    Status: {request_result.get('status_code')}")
        logging.info(f"    Load time: {request_result.get('load_time_ms')}ms")
        logging.info(f"    Size: {request_result.get('page_size_kb')}KB")
        logging.info(f"    Title: {request_result.get('title', 'No title')}")
        logging.info(f"    Final URL: {request_result.get('redirect_url')}")
    else:
        logging.info(f"    Error: {request_result.get('error', 'Unknown error')}")
    
    # Test with playwright
    logging.info(f"  Testing with Playwright...")
    browser_result = test_with_playwright(url)
    
    browser_success = browser_result.get('success', False)
    logging.info(f"  Playwright result: {'SUCCESS' if browser_success else 'FAILED'}")
    if browser_success:
        logging.info(f"    Status: {browser_result.get('status_code')}")
        logging.info(f"    Load time: {browser_result.get('load_time_ms')}ms")
        logging.info(f"    Title: {browser_result.get('title', 'No title')}")
        logging.info(f"    Final URL: {browser_result.get('final_url')}")
        logging.info(f"    Bot detected: {'Yes' if browser_result.get('bot_detected') else 'No'}")
    else:
        logging.info(f"    Error: {browser_result.get('error', 'Unknown error')}")
    
    # Get recommendations
    recommendation = recommend_scrape_method(request_result, browser_result)
    logging.info(f"  Recommendation: {recommendation['recommended_method']}")
    for handling in recommendation['special_handling']:
        logging.info(f"    - {handling}")
    
    # Prepare result summary
    result = {
        'url': url,
        'status': 'Success' if request_success or browser_success else 'Failed',
        'request_access': 'Yes' if request_success else 'No',
        'request_status_code': request_result.get('status_code', 0),
        'browser_access': 'Yes' if browser_success else 'No',
        'bot_detection': 'Yes' if browser_result.get('bot_detected') else 'No',
        'load_time_ms': request_result.get('load_time_ms', 0) if request_success else browser_result.get('load_time_ms', 0),
        'page_size_kb': request_result.get('page_size_kb', 0),
        'title': request_result.get('title', browser_result.get('title', 'Unknown')),
        'redirect_url': request_result.get('redirect_url', browser_result.get('final_url', url)),
        'scrape_method': recommendation['recommended_method'],
        'special_handling': '; '.join(recommendation['special_handling'])
    }
    
    logging.info(f"  Test completed for {url}")
    logging.info("-" * 80)
    
    # Add delay between tests to avoid overloading servers
    delay = random.uniform(2, 5)
    logging.info(f"Waiting {delay:.1f} seconds before next test...")
    time.sleep(delay)
    
    return result

def batch_test_sites(urls_file, max_sites=None):
    """Test multiple sites from a JSON file"""
    logging.info(f"Starting batch test from {urls_file}")
    
    # Load URLs from JSON
    try:
        with open(urls_file, 'r') as f:
            data = json.load(f)
            urls = data.get('business_sites', [])
            
        if not urls:
            logging.error("No URLs found in the JSON file")
            return []
        
        logging.info(f"Loaded {len(urls)} URLs from JSON file")
        
        # Limit number of sites to test if specified
        if max_sites and max_sites > 0:
            urls = urls[:max_sites]
            logging.info(f"Testing first {max_sites} URLs")
        
        # Test each site
        results = []
        for i, url in enumerate(urls):
            logging.info(f"Testing site {i+1}/{len(urls)}: {url}")
            result = test_site(url)
            results.append(result)
        
        return results
        
    except Exception as e:
        logging.error(f"Error in batch testing: {str(e)}")
        return []

def main():
    """Main function"""
    urls_file = "business_sites.json"
    
    print("=" * 80)
    print("Website Accessibility Tester")
    print("=" * 80)
    print(f"This tool will test the accessibility of websites listed in {urls_file}")
    print(f"Results will be saved to {log_file}")
    print("=" * 80)
    
    # Ask if user wants to limit the number of sites to test
    try:
        max_sites_input = input("Enter maximum number of sites to test (or press Enter for all): ")
        max_sites = int(max_sites_input) if max_sites_input.strip() else None
    except ValueError:
        print("Invalid input, testing all sites")
        max_sites = None
    
    print("\nStarting tests...")
    start_time = time.time()
    
    # Run the batch test
    results = batch_test_sites(urls_file, max_sites)
    
    # Create CSV report
    if results:
        csv_file = create_csv_report(results)
        
        # Print summary
        elapsed_time = time.time() - start_time
        print("\n" + "=" * 80)
        print(f"Testing completed for {len(results)} sites in {elapsed_time:.1f} seconds")
        print(f"Log file: {log_file}")
        print(f"CSV report: {csv_file}")
        print("\nSummary:")
        print(f"  - Accessible via Requests: {sum(1 for r in results if r['request_access'] == 'Yes')}/{len(results)}")
        print(f"  - Accessible via Browser: {sum(1 for r in results if r['browser_access'] == 'Yes')}/{len(results)}")
        print(f"  - Bot Detection present: {sum(1 for r in results if r['bot_detection'] == 'Yes')}/{len(results)}")
        
        # Group by recommended method
        methods = {}
        for r in results:
            method = r['scrape_method']
            methods[method] = methods.get(method, 0) + 1
        
        print("\nRecommended scraping methods:")
        for method, count in methods.items():
            print(f"  - {method}: {count} sites")
    else:
        print("No results generated. Check the log file for errors.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
