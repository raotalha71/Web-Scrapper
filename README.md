# Advanced Web Scraping Framework

A comprehensive web scraping framework that tests website accessibility and employs multiple scraping techniques to handle a variety of websites, including those with bot protection.

## Project Structure

```
├── batch_scraper.py           # Main scraper for accessible sites
├── test_site_access.py        # Tests website accessibility and recommends scraping methods
├── advanced_scraper.py        # Advanced browser-based scraper for challenging sites
├── proxy_scraper.py           # Multi-method proxy-based scraper with stealth techniques
├── generate_combined_report.py # Creates a comprehensive scraping report
├── user_agents.txt            # List of user agents for rotating requests
├── run_scraper.bat            # Convenience script to run the standard scraper
├── run_advanced_scraper.bat   # Convenience script to run the advanced scraper
├── run_proxy_scraper.bat      # Convenience script to run the proxy-based scraper
├── run_generate_report.bat    # Convenience script to generate the combined report
├── config/                    # Configuration files
│   └── scraper_config.json    # Scraper configuration
├── data/                      # Scraped data output directory
├── logs/                      # Log files and site access reports
├── screenshots/               # Screenshots from browser-based scraping
└── temp/                      # Temporary files
```

## Overview

This framework provides a comprehensive approach to web scraping, especially for challenging websites:

1. **Site Testing**: `test_site_access.py` analyzes each website to determine the best approach
2. **Basic Scraping**: `batch_scraper.py` handles easily accessible sites
3. **Advanced Scraping**: `advanced_scraper.py` uses browser automation for more difficult sites
4. **Proxy-based Scraping**: `proxy_scraper.py` employs multiple methods with stealth techniques
5. **Reporting**: `generate_combined_report.py` creates a comprehensive analysis of all scraping results

## Scraping Methodology

The framework employs a multi-tiered approach to handle different types of websites:

### Tier 1: Basic Requests
- Uses simple requests with BeautifulSoup for easily accessible sites
- Fast and efficient for sites without protection

### Tier 2: Enhanced Requests
- Uses custom headers, cookies, and referrers
- Handles sites with basic access restrictions

### Tier 3: Browser Automation
- Uses Playwright for sites requiring JavaScript
- Handles complex sites with interactive elements

### Tier 4: Stealth Techniques
- Advanced browser fingerprint masking
- Custom user agent rotation
- Anti-bot detection measures
- Handling of cookies and timeouts

### Tier 5: Domain Verification
- Checks alternative domain formats
- Handles cases where domains have changed or are mistyped

## How to Use

### Prerequisites

- Python 3.8+ (Python 3.9+ recommended)
- pip (Python package installer)
- Git (for cloning the repository)

### Installation & Setup


#### Step 2: Create Virtual Environment (Recommended)
Creating a virtual environment is **highly recommended** to avoid dependency conflicts with other Python projects.

**For Windows (PowerShell/Command Prompt):**
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify activation (you should see (.venv) in your prompt)
```

**For Windows (Git Bash):**
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
source .venv/Scripts/activate
```

**For macOS/Linux:**
```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate
```

#### Step 3: Install Dependencies
Once your virtual environment is activated, install the required packages:

```bash
# Install all required packages
pip install -r requirements.txt

# Install Playwright browsers (required for browser automation)
playwright install

# Verify installation
python -c "import requests, bs4, playwright, pandas; print('All packages installed successfully!')"
```

#### Step 4: Verify Setup
Test that everything is working:
```bash
python test_site_access.py
```

### Package Requirements

The following packages will be installed via `requirements.txt`:

#### Core Dependencies:
- **requests** (>=2.31.0) - HTTP library for making web requests
- **beautifulsoup4** (>=4.12.0) - HTML/XML parsing library
- **playwright** (>=1.40.0) - Browser automation library
- **pandas** (>=2.0.0) - Data manipulation and analysis

#### Additional Dependencies:
- **lxml** (>=4.9.0) - Fast XML and HTML parser
- **selenium** (>=4.15.0) - Alternative browser automation (optional)
- **fake-useragent** (>=1.4.0) - Generate random user agents
- **urllib3** (>=2.0.0) - Advanced HTTP client
- **certifi** (>=2023.7.22) - Certificate bundle
- **tkinter** - GUI framework (usually included with Python)

#### Optional Dependencies:
- **html5lib** (>=1.1) - Pure-python HTML parser
- **httpx** (>=0.25.0) - Async HTTP client

### Manual Installation (Alternative)
If you prefer to install packages individually:

```bash
# Core packages
pip install requests>=2.31.0
pip install beautifulsoup4>=4.12.0
pip install playwright>=1.40.0
pip install pandas>=2.0.0

# Additional packages
pip install lxml>=4.9.0
pip install fake-useragent>=1.4.0

# Install Playwright browsers
playwright install
```

### Virtual Environment Management

**To deactivate the virtual environment:**
```bash
deactivate
```

**To reactivate later:**
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**To remove the virtual environment:**
```bash
# First deactivate
deactivate

# Then remove the folder
rm -rf .venv    # macOS/Linux
rmdir /s .venv  # Windows
```

### Basic Usage


### Using Convenience Scripts

For Windows users, batch files are provided for easier execution:

- `run_scraper.bat` - Runs the standard scraper
- `run_advanced_scraper.bat` - Runs the advanced scraper
- `run_proxy_scraper.bat` - Runs the proxy-based scraper
- `run_generate_report.bat` - Generates the combined report

## Output Files

- `scraped_data.csv` - Data from standard scraping
- `advanced_scraped_data.csv` - Data from advanced scraping
- `proxy_scraped_data.csv` - Data from proxy-based scraping
- `combined_report_YYYYMMDD_HHMMSS.csv` - Comprehensive analysis of all scraping results
- `logs/*.log` - Detailed logs of the scraping process
- `screenshots/*.png` - Screenshots from browser-based scraping

## Handling Challenging Websites

For websites that are particularly difficult to scrape, the framework employs several strategies:

1. **Bot Detection Bypass**:
   - Browser fingerprint randomization
   - Human-like mouse movements and scrolling
   - Delayed execution and random waits

2. **Error Handling**:
   - Automatic retries with different methods
   - Progressive fallback to more advanced techniques
   - Detailed error logging for analysis

3. **Domain Verification**:
   - Checks for alternative domain formats
   - Handles redirects and domain changes

## Extending the Framework

To add new scraping methods:

1. Create a new method in the appropriate scraper class
2. Update the scrape_url_with_multiple_attempts method to include your new method
3. Make sure to handle errors and return standardized data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This framework is for educational purposes only. Always respect website terms of service, robots.txt files, and legal restrictions when scraping websites. Use responsibly and ethically.
