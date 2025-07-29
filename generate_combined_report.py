import pandas as pd
import os
import sys
import datetime
import logging
import json

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"combined_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def generate_combined_report(site_access_report, standard_data_csv, advanced_data_csv=None, proxy_data_csv=None, output_file=None):
    """
    Generate a combined report of all scraping results
    
    Args:
        site_access_report: Path to the site access report CSV
        standard_data_csv: Path to the standard scraped data CSV
        advanced_data_csv: Path to the advanced scraped data CSV (optional)
        proxy_data_csv: Path to the proxy scraped data CSV (optional)
        output_file: Path to save the combined report (optional)
    
    Returns:
        DataFrame with combined report
    """
    if not os.path.exists(site_access_report):
        logging.error(f"Site access report not found: {site_access_report}")
        return None
    
    if not os.path.exists(standard_data_csv):
        logging.error(f"Standard data CSV not found: {standard_data_csv}")
        return None
    
    # Read site access report
    try:
        site_df = pd.read_csv(site_access_report)
        logging.info(f"Loaded site access report with {len(site_df)} sites")
    except Exception as e:
        logging.error(f"Error reading site access report: {e}")
        return None
    
    # Read standard data
    try:
        standard_df = pd.read_csv(standard_data_csv)
        logging.info(f"Loaded standard data with {len(standard_df)} entries")
    except Exception as e:
        logging.error(f"Error reading standard data CSV: {e}")
        return None
    
    # Read advanced data if available
    advanced_df = None
    if advanced_data_csv and os.path.exists(advanced_data_csv):
        try:
            advanced_df = pd.read_csv(advanced_data_csv)
            logging.info(f"Loaded advanced data with {len(advanced_df)} entries")
        except Exception as e:
            logging.warning(f"Error reading advanced data CSV: {e}")
    
    # Read proxy data if available
    proxy_df = None
    if proxy_data_csv and os.path.exists(proxy_data_csv):
        try:
            proxy_df = pd.read_csv(proxy_data_csv)
            logging.info(f"Loaded proxy data with {len(proxy_df)} entries")
        except Exception as e:
            logging.warning(f"Error reading proxy data CSV: {e}")
    
    # Create combined report structure
    report_data = []
    
    # Process each site from the site access report
    for _, row in site_df.iterrows():
        url = row['url']
        site_data = {
            'url': url,
            'domain': row.get('domain', ''),
            'test_request_access': row.get('request_access', 'No'),
            'test_browser_access': row.get('browser_access', 'No'),
            'test_scrape_method': row.get('scrape_method', ''),
            'test_bot_detection': row.get('bot_detection', 'No'),
            'standard_scraping_success': 'No',
            'standard_scraping_method': '',
            'advanced_scraping_success': 'No',
            'advanced_scraping_method': '',
            'proxy_scraping_success': 'No',
            'proxy_scraping_method': '',
            'final_status': 'Not Scraped',
            'content_available': 'No',
            'screenshot_available': 'No',
            'notes': row.get('special_handling', '')
        }
        
        # Check if standard scraping was successful
        standard_match = standard_df[standard_df['url'] == url]
        if not standard_match.empty:
            site_data['standard_scraping_success'] = 'Yes'
            site_data['standard_scraping_method'] = standard_match.iloc[0].get('scraper_method', '')
            site_data['final_status'] = 'Scraped (Standard)'
            site_data['content_available'] = 'Yes'
        
        # Check if advanced scraping was successful
        if advanced_df is not None:
            advanced_match = advanced_df[advanced_df['url'] == url]
            if not advanced_match.empty:
                site_data['advanced_scraping_success'] = 'Yes'
                site_data['advanced_scraping_method'] = advanced_match.iloc[0].get('scraper_method', '')
                if site_data['final_status'] == 'Not Scraped':
                    site_data['final_status'] = 'Scraped (Advanced)'
                    site_data['content_available'] = 'Yes'
        
        # Check if proxy scraping was successful
        if proxy_df is not None:
            proxy_match = proxy_df[proxy_df['url'] == url]
            if not proxy_match.empty and proxy_match.iloc[0].get('successful_method', '') != 'none':
                site_data['proxy_scraping_success'] = 'Yes'
                site_data['proxy_scraping_method'] = proxy_match.iloc[0].get('successful_method', '')
                if site_data['final_status'] == 'Not Scraped':
                    site_data['final_status'] = 'Scraped (Proxy)'
                    site_data['content_available'] = 'Yes'
                
                # Check if screenshot is available
                if not pd.isna(proxy_match.iloc[0].get('screenshot_path', '')) and proxy_match.iloc[0].get('screenshot_path', '') != '':
                    site_data['screenshot_available'] = 'Yes'
        
        report_data.append(site_data)
    
    # Create DataFrame
    report_df = pd.DataFrame(report_data)
    
    # Sort by URL
    report_df = report_df.sort_values('url')
    
    # Save to file if specified
    if output_file:
        report_df.to_csv(output_file, index=False)
        logging.info(f"Combined report saved to {output_file}")
    
    # Print summary
    total_sites = len(report_df)
    scraped_sites = len(report_df[report_df['final_status'].str.startswith('Scraped')])
    
    print("\n" + "=" * 80)
    print("COMBINED SCRAPING RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total sites analyzed: {total_sites}")
    print(f"Successfully scraped: {scraped_sites} ({scraped_sites/total_sites*100:.1f}%)")
    print(f"Not scraped: {total_sites - scraped_sites} ({(total_sites - scraped_sites)/total_sites*100:.1f}%)")
    print("\nScraping methods breakdown:")
    
    for method_type, method_col in [
        ('Standard', 'standard_scraping_method'), 
        ('Advanced', 'advanced_scraping_method'), 
        ('Proxy', 'proxy_scraping_method')
    ]:
        method_counts = report_df[report_df[f'{method_type.lower()}_scraping_success'] == 'Yes'][method_col].value_counts()
        if not method_counts.empty:
            print(f"\n{method_type} methods:")
            for method, count in method_counts.items():
                print(f"  - {method}: {count} sites")
    
    print("\nScreenshot availability:")
    screenshot_count = len(report_df[report_df['screenshot_available'] == 'Yes'])
    print(f"  - Sites with screenshots: {screenshot_count} ({screenshot_count/total_sites*100:.1f}%)")
    
    print("=" * 80)
    
    return report_df

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python generate_combined_report.py <site_access_report.csv> <standard_data.csv> [advanced_data.csv] [proxy_data.csv]")
        return
    
    site_access_report = sys.argv[1]
    standard_data_csv = sys.argv[2]
    advanced_data_csv = sys.argv[3] if len(sys.argv) > 3 else None
    proxy_data_csv = sys.argv[4] if len(sys.argv) > 4 else None
    
    # Generate output filename
    output_file = f"combined_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    print("=" * 80)
    print("GENERATING COMBINED SCRAPING REPORT")
    print("=" * 80)
    print(f"Site access report: {site_access_report}")
    print(f"Standard data: {standard_data_csv}")
    if advanced_data_csv:
        print(f"Advanced data: {advanced_data_csv}")
    if proxy_data_csv:
        print(f"Proxy data: {proxy_data_csv}")
    print(f"Output file: {output_file}")
    
    # Generate report
    generate_combined_report(
        site_access_report=site_access_report,
        standard_data_csv=standard_data_csv,
        advanced_data_csv=advanced_data_csv,
        proxy_data_csv=proxy_data_csv,
        output_file=output_file
    )

if __name__ == "__main__":
    main()
