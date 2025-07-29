import os
import sys
import json
import time
import datetime
import subprocess
import pandas as pd
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import webbrowser

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure main logger
log_file = os.path.join(log_dir, f"unified_scraper_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

# Create console handler with a higher log level
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

logger = logging.getLogger("UnifiedScraper")
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)

class UnifiedScraper:
    """Unified scraper that handles the entire process from start to finish"""
    
    def __init__(self, input_file=None, output_dir=None):
        self.input_file = input_file
        self.output_dir = output_dir or os.getcwd()
        self.site_access_report = None
        self.standard_data_file = os.path.join(self.output_dir, "scraped_data.csv")
        self.advanced_data_file = os.path.join(self.output_dir, "advanced_scraped_data.csv")
        self.proxy_data_file = os.path.join(self.output_dir, "proxy_scraped_data.csv")
        self.combined_report_file = None
        self.log_file = log_file
        self.progress = 0
        self.status_message = "Ready"
        self.running = False
        self.process_thread = None
        
    def select_input_file(self):
        """Select the input JSON file with websites to scrape"""
        self.input_file = filedialog.askopenfilename(
            title="Select Input JSON File",
            filetypes=[("JSON files", "*.json")]
        )
        return self.input_file
    
    def run_site_access_test(self):
        """Run the site access test script"""
        if not self.input_file:
            logger.error("No input file selected")
            return False
            
        logger.info(f"Running site access test on {self.input_file}")
        self.status_message = "Testing site accessibility..."
        
        # Run the test_site_access.py script
        try:
            result = subprocess.run(
                ["python", "test_site_access.py", self.input_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Site access test failed: {result.stderr}")
                return False
                
            # Find the generated report file
            report_files = [f for f in os.listdir(log_dir) if f.startswith("site_access_report_") and f.endswith(".csv")]
            if not report_files:
                logger.error("No site access report generated")
                return False
                
            # Sort by creation time and get the most recent
            report_files.sort(key=lambda x: os.path.getctime(os.path.join(log_dir, x)), reverse=True)
            self.site_access_report = os.path.join(log_dir, report_files[0])
            logger.info(f"Site access report generated: {self.site_access_report}")
            return True
            
        except Exception as e:
            logger.error(f"Error running site access test: {e}")
            return False
    
    def run_standard_scraper(self):
        """Run the standard batch scraper script"""
        if not self.site_access_report:
            logger.error("No site access report available")
            return False
            
        logger.info(f"Running standard scraper on {self.site_access_report}")
        self.status_message = "Running standard scraper..."
        
        # Run the batch_scraper.py script
        try:
            result = subprocess.run(
                ["python", "batch_scraper.py", self.site_access_report],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Standard scraper failed: {result.stderr}")
                return False
                
            if not os.path.exists(self.standard_data_file):
                logger.warning("Standard scraper did not generate output file")
                return False
                
            logger.info(f"Standard scraping completed: {self.standard_data_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error running standard scraper: {e}")
            return False
    
    def run_advanced_scraper(self):
        """Run the advanced scraper script"""
        if not self.site_access_report:
            logger.error("No site access report available")
            return False
            
        logger.info(f"Running advanced scraper on {self.site_access_report}")
        self.status_message = "Running advanced scraper..."
        
        # Run the advanced_scraper.py script
        try:
            result = subprocess.run(
                ["python", "advanced_scraper.py", self.site_access_report],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Advanced scraper failed: {result.stderr}")
                return False
                
            if not os.path.exists(self.advanced_data_file):
                logger.warning("Advanced scraper did not generate output file")
                return False
                
            logger.info(f"Advanced scraping completed: {self.advanced_data_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error running advanced scraper: {e}")
            return False
    
    def run_proxy_scraper(self):
        """Run the proxy-based scraper script"""
        if not self.site_access_report:
            logger.error("No site access report available")
            return False
            
        logger.info(f"Running proxy scraper on {self.site_access_report}")
        self.status_message = "Running proxy scraper..."
        
        # Run the proxy_scraper.py script
        try:
            result = subprocess.run(
                ["python", "proxy_scraper.py", self.site_access_report],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Proxy scraper failed: {result.stderr}")
                return False
                
            if not os.path.exists(self.proxy_data_file):
                logger.warning("Proxy scraper did not generate output file")
                return False
                
            logger.info(f"Proxy scraping completed: {self.proxy_data_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error running proxy scraper: {e}")
            return False
    
    def generate_combined_report(self):
        """Generate combined report of all scraping results"""
        if not self.site_access_report:
            logger.error("No site access report available")
            return False
            
        logger.info("Generating combined report")
        self.status_message = "Generating combined report..."
        
        # Check which data files exist
        args = ["python", "generate_combined_report.py", self.site_access_report]
        
        if os.path.exists(self.standard_data_file):
            args.append(self.standard_data_file)
        else:
            logger.warning("Standard data file not found")
            return False
            
        if os.path.exists(self.advanced_data_file):
            args.append(self.advanced_data_file)
        else:
            args.append("")  # Empty string placeholder
            
        if os.path.exists(self.proxy_data_file):
            args.append(self.proxy_data_file)
        
        # Run the generate_combined_report.py script
        try:
            result = subprocess.run(
                args,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Combined report generation failed: {result.stderr}")
                return False
                
            # Find the generated report file
            report_files = [f for f in os.listdir() if f.startswith("combined_report_") and f.endswith(".csv")]
            if not report_files:
                logger.error("No combined report generated")
                return False
                
            # Sort by creation time and get the most recent
            report_files.sort(key=lambda x: os.path.getctime(x), reverse=True)
            self.combined_report_file = report_files[0]
            logger.info(f"Combined report generated: {self.combined_report_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating combined report: {e}")
            return False
    
    def run_all(self):
        """Run the entire scraping process in sequence"""
        if not self.input_file:
            logger.error("No input file selected")
            return False
        
        self.running = True
        self.progress = 0
        self.status_message = "Starting scraping process..."
        
        # Step 1: Run site access test
        if self.run_site_access_test():
            self.progress = 20
        else:
            self.status_message = "Site access test failed"
            self.running = False
            return False
        
        # Step 2: Run standard scraper
        if self.run_standard_scraper():
            self.progress = 40
        else:
            logger.warning("Standard scraper failed, continuing with process")
        
        # Step 3: Run advanced scraper
        if self.run_advanced_scraper():
            self.progress = 60
        else:
            logger.warning("Advanced scraper failed, continuing with process")
        
        # Step 4: Run proxy scraper
        if self.run_proxy_scraper():
            self.progress = 80
        else:
            logger.warning("Proxy scraper failed, continuing with process")
        
        # Step 5: Generate combined report
        if self.generate_combined_report():
            self.progress = 100
            self.status_message = "Scraping process completed successfully"
            logger.info("Scraping process completed successfully")
        else:
            self.status_message = "Combined report generation failed"
            self.running = False
            return False
        
        self.running = False
        return True
    
    def start_scraping_thread(self):
        """Start the scraping process in a separate thread"""
        if self.running:
            return
            
        self.process_thread = threading.Thread(target=self.run_all)
        self.process_thread.start()
    
    def get_progress(self):
        """Get the current progress percentage"""
        return self.progress
    
    def get_status(self):
        """Get the current status message"""
        return self.status_message
    
    def is_running(self):
        """Check if the scraping process is running"""
        return self.running
    
    def open_report(self):
        """Open the combined report in the default application"""
        if self.combined_report_file and os.path.exists(self.combined_report_file):
            try:
                webbrowser.open(self.combined_report_file)
            except Exception as e:
                logger.error(f"Error opening report: {e}")
                return False
            return True
        return False
    
    def open_log(self):
        """Open the log file in the default application"""
        if os.path.exists(self.log_file):
            try:
                webbrowser.open(self.log_file)
            except Exception as e:
                logger.error(f"Error opening log: {e}")
                return False
            return True
        return False

class UnifiedScraperGUI:
    """GUI for the unified scraper"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Unified Web Scraper")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.scraper = UnifiedScraper()
        
        self.create_widgets()
        self.update_timer = None
        self.start_update_timer()
    
    def create_widgets(self):
        """Create the GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Unified Web Scraper", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Input file frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        input_label = ttk.Label(input_frame, text="Input File:")
        input_label.pack(side=tk.LEFT, padx=5)
        
        self.input_var = tk.StringVar()
        input_entry = ttk.Entry(input_frame, textvariable=self.input_var, width=50)
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = ttk.Button(input_frame, text="Browse", command=self.browse_input)
        browse_button.pack(side=tk.LEFT, padx=5)
        
        # Start button
        self.start_button = ttk.Button(main_frame, text="Start Scraping", command=self.start_scraping)
        self.start_button.pack(pady=10)
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        status_label.pack(fill=tk.X, pady=5)
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        self.view_report_button = ttk.Button(buttons_frame, text="View Report", command=self.view_report, state=tk.DISABLED)
        self.view_report_button.pack(side=tk.LEFT, padx=5)
        
        self.view_log_button = ttk.Button(buttons_frame, text="View Log", command=self.view_log)
        self.view_log_button.pack(side=tk.LEFT, padx=5)
        
        self.exit_button = ttk.Button(buttons_frame, text="Exit", command=self.root.destroy)
        self.exit_button.pack(side=tk.RIGHT, padx=5)
    
    def browse_input(self):
        """Browse for input file"""
        file_path = self.scraper.select_input_file()
        if file_path:
            self.input_var.set(file_path)
    
    def start_scraping(self):
        """Start the scraping process"""
        if self.scraper.is_running():
            return
            
        # Get input file from entry
        input_file = self.input_var.get()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file")
            return
            
        self.scraper.input_file = input_file
        
        # Disable start button
        self.start_button.config(state=tk.DISABLED)
        self.view_report_button.config(state=tk.DISABLED)
        
        # Start scraping in a separate thread
        self.scraper.start_scraping_thread()
    
    def update_gui(self):
        """Update the GUI with current progress and status"""
        if self.scraper:
            # Update progress bar
            self.progress_var.set(self.scraper.get_progress())
            
            # Update status message
            self.status_var.set(self.scraper.get_status())
            
            # Check if process is complete
            if not self.scraper.is_running() and self.scraper.get_progress() == 100:
                self.start_button.config(state=tk.NORMAL)
                self.view_report_button.config(state=tk.NORMAL)
                messagebox.showinfo("Complete", "Scraping process completed successfully!")
            elif not self.scraper.is_running() and self.scraper.get_progress() > 0:
                self.start_button.config(state=tk.NORMAL)
                messagebox.showerror("Error", "Scraping process failed. Check log for details.")
        
        # Schedule next update
        self.update_timer = self.root.after(100, self.update_gui)
    
    def start_update_timer(self):
        """Start the timer for updating the GUI"""
        self.update_timer = self.root.after(100, self.update_gui)
    
    def view_report(self):
        """View the generated report"""
        if not self.scraper.open_report():
            messagebox.showerror("Error", "No report available to view")
    
    def view_log(self):
        """View the log file"""
        if not self.scraper.open_log():
            messagebox.showerror("Error", "No log file available to view")

def run_gui():
    """Run the GUI application"""
    root = tk.Tk()
    app = UnifiedScraperGUI(root)
    root.mainloop()

def run_cli(input_file):
    """Run the CLI application"""
    scraper = UnifiedScraper(input_file)
    
    print("=" * 80)
    print("UNIFIED WEB SCRAPER")
    print("=" * 80)
    print(f"Input file: {input_file}")
    print(f"Log file: {scraper.log_file}")
    print("=" * 80)
    
    print("Starting scraping process...")
    
    if scraper.run_all():
        print("\nScraping process completed successfully!")
        print(f"Combined report: {scraper.combined_report_file}")
        print(f"Log file: {scraper.log_file}")
    else:
        print("\nScraping process failed. Check log for details.")
        print(f"Log file: {scraper.log_file}")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        # CLI mode
        input_file = sys.argv[1]
        run_cli(input_file)
    else:
        # GUI mode
        run_gui()

if __name__ == "__main__":
    main()
