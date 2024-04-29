<h2>Website Scraper</h2>

This is a small project that can be used to collect and scrape job search information from Linkedin and Indeed.

A Jupyter Notebook is included that breaks down each step with the code.

Otherwise, a ```Job_Scraper``` class exists in main.py that can be used to scrape website information.

Instantiate a ```Job_Scraper``` object and call the ```scrape_jobs()``` method with your required parameters.

Data will be collected in a ```self.jobs_df``` pandas dataframe for any additional data processing.

Once finished, used the ```write_data()``` method to save the file to a csv.
