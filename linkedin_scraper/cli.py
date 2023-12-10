import time
import sys
import click
import logging

from linkedin_scraper import ScraperController
from linkedin_scraper.utils import read_csv
from linkedin_scraper.config import LOG_LEVEL, LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


@click.command()
@click.argument("input_csv", type=click.Path(exists=True))
@click.argument("output_file_path", type=click.Path(exists=False))
@click.option("--progress/--no-progress", default=True)
def scrape_companies_csv(input_csv, output_file_path, progress):
    """
    INPUT_CSV: Path to a .csv file containing company names

    OUTPUT_FILE_PATH: Path to the output file to be generated (must not exist)
    """
    # Enable stdout logging only if the progress bar is not enabled.
    if not progress:
        logging.basicConfig(
            format=f"[%(levelname)s] %(asctime)s %(message)s", level=LOG_LEVEL
        )

    company_names = read_csv(fname=input_csv)

    logger.info("Starting scraping session")
    scraper_controller = ScraperController(show_progress=progress)

    try:
        results = scraper_controller.scrape(company_names_list=company_names)
    except KeyboardInterrupt:
        # gracefully stop the child processes
        scraper_controller.stop()
        time.sleep(1)
        sys.exit(0)

    # Export the results in the output path
    with open(output_file_path, "w") as f:
        f.write("company_name, status, linkedin_url, employee_count\n")
        for k in results.keys():
            if results[k]["status"] == "success":
                f.write(
                    f"{k}, {results[k]['status']}, {results[k]['linkedin_url']}, {results[k]['employee_count']}\n"
                )

    logger.info(f"\nScraping finished. Results saved to: {output_file_path}")
