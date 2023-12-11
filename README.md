### INSTALL:
`pip install .`

### USAGE:

After installing, execute the command line tool:

`> linkedin_scraper input_data.csv output.csv`

Use `linkedin_scraper --help` to learn the additional options

If instead of a command line tool you need to use this as a library, to integrate with an existing app, check the documentation
for the `ScraperController` class.

The following settings can be changed by setting them in environment variables:

`LOG_LEVEL`: Set the logging level, default is INFO

`LINKEDIN_SCRAPER_PROXY`: Proxy to use for google scraping (highly recommended for google scraping).

`LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY`: Number of concurrent Google scrape instances, default: 20

`LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY`: Number of concurrent Linkedin (playwright) scrape instances, default: 10

`LINKEDIN_SCRAPER_MAX_GOOGLE_RETRY`: Maximum number of times a Google scrape task should be retried. (This is to account for Bot detection, 429s) 


### To run unit tests:

`pip install -e .`

`pip install mock`

`python -m unittest discover -v .`


### To generate the html documentation:

`pip install sphinx sphinx_rtd_theme`

`cd docs && make clean html`
