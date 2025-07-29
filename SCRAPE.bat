@echo off
chcp 65001 >nul
title Business Website Scraper - Choose Your Mode

echo.
echo ================================================================================
echo                          BUSINESS WEBSITE SCRAPER
echo                           Choose Your Experience
echo ================================================================================
echo.
echo Select how you want to run the scraper:
echo.
echo   [1] 🤖 CLI Mode (Fully Automated)
echo       • No user interaction needed
echo       • Runs completely automatically
echo       • Perfect for batch processing
echo       • Faster execution
echo.
echo   [2] ❌ Cancel
echo.
echo ================================================================================

:choice
set /p MODE="Enter your choice (1 OR 2): "

if "%MODE%"=="1" goto cli_mode
if "%MODE%"=="2" goto cancel
echo Invalid choice! Please enter 1, or 2
goto choice

:cli_mode
echo.
echo 🤖 Starting CLI Automation Mode...
echo ================================================================================
echo.
echo This will automatically scrape all 31 business websites using:
echo   • Site accessibility testing
echo   • Standard HTTP scraping
echo   • Advanced browser automation  
echo   • Proxy-based scraping for protected sites
echo   • Comprehensive report generation
echo.
echo ⏱️  Estimated time: 15-25 minutes
echo 📁 Results will be saved to Excel and CSV files
echo 📋 Detailed logs will be available in logs\ folder
echo.
echo Press Ctrl+C anytime to cancel the process
echo.
pause

REM Activate virtual environment
echo.
echo [INITIALIZING] Activating Python environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Failed to activate virtual environment!
    echo    Please run setup.bat first to create the environment.
    echo.
    pause
    exit /b 1
)
echo ✅ Environment activated successfully
echo.

REM Run site access test with no interaction
echo [STEP 1/5] Testing website accessibility...
echo | python test_site_access.py business_sites.json
if errorlevel 1 (
    echo ❌ ERROR: Site access testing failed!
    pause
    exit /b 1
)
echo ✅ Site accessibility testing completed
echo.

REM Find the latest report
echo [STEP 2/5] Finding latest accessibility report...
for /f %%i in ('dir /b logs\site_access_report_*.csv 2^>nul ^| sort /r') do set LATEST_REPORT=%%i & goto :found_report
:found_report
if not defined LATEST_REPORT (
    echo ❌ ERROR: No site access report found!
    pause
    exit /b 1
)
echo ✅ Found report: %LATEST_REPORT%
echo.

REM Run batch scraper (PRIORITY - handles 19 websites successfully)
echo [STEP 3/6] Running batch web scraper (PRIMARY METHOD)...
echo          This will scrape ~19 accessible websites with standard HTTP methods
python batch_scraper.py "logs\%LATEST_REPORT%"
if errorlevel 1 (
    echo ⚠️  WARNING: Batch scraping had some issues, continuing...
) else (
    echo ✅ Batch scraping completed successfully
)
echo.

REM Run proxy scraper (SECONDARY - for protected/difficult sites) 
echo [STEP 4/6] Running proxy-based scraper (SECONDARY METHOD)...
echo          This will attempt to scrape remaining protected sites
python proxy_scraper.py "logs\%LATEST_REPORT%"
if errorlevel 1 (
    echo ⚠️  WARNING: Proxy scraping had some issues, continuing...
) else (
    echo ✅ Proxy scraping completed successfully
)
echo.

REM Merge CSV files (batch + proxy, batch has priority)
echo [STEP 5/6] Merging scraped data...
echo          Combining batch and proxy results (batch data prioritized)
python merge_csv.py
if errorlevel 1 (
    echo ⚠️  WARNING: CSV merge had some issues, continuing...
) else (
    echo ✅ CSV files merged successfully
)
echo.

REM Generate comprehensive Excel report
echo [STEP 6/6] Generating comprehensive Excel report...
echo          Creating final Excel report with all analysis
python generate_combined_report.py
if errorlevel 1 (
    echo ❌ ERROR: Failed to generate Excel report!
    pause
    exit /b 1
)
echo ✅ Excel report generated successfully
echo.

echo ================================================================================
echo                              SCRAPING COMPLETED!
echo ================================================================================
echo.
echo 🎉 Results have been saved to:
if exist combined_business_data_report.xlsx (
    echo    ✅ combined_business_data_report.xlsx ^(MAIN EXCEL REPORT^)
)
if exist final_combined_data_*.csv (
    for %%f in (final_combined_data_*.csv) do echo    ✅ %%f ^(MERGED CSV DATA^)
)
if exist scraped_data.csv (
    echo    ✅ scraped_data.csv ^(Batch scraper - 19 sites^)
)
if exist proxy_scraped_data.csv (
    echo    ✅ proxy_scraped_data.csv ^(Proxy scraper - additional sites^)
)
echo.
echo 📁 Check the logs\ folder for detailed operation logs
echo.

REM Ask if user wants to open the main report
set /p OPEN_REPORT="Would you like to open the main Excel report now? (y/n): "
if /i "%OPEN_REPORT%"=="y" (
    if exist combined_business_data_report.xlsx (
        echo.
        echo 📖 Opening report...
        start combined_business_data_report.xlsx
    ) else (
        echo ❌ Main report file not found!
    )
)

echo.
echo 🎯 TIP: The Excel file contains all results organized by scraping method
echo    and includes site accessibility analysis and recommendations.
goto end

:cancel
echo.
echo ❌ Operation cancelled by user.
goto end

:end
echo.
echo ================================================================================
echo Press any key to exit...
pause >nul
