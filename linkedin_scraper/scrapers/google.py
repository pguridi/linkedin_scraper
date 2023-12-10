import yagooglesearch


from linkedin_scraper.scrapers.base import BaseScraperWorker
from linkedin_scraper.config import LINKEDIN_SCRAPER_PROXY
from linkedin_scraper.exceptions import ScrapingError


def run_google_query(company_name):
    """This method performs the actual google query"""
    query = f"{company_name} site:https://www.linkedin.com/company/"
    client = yagooglesearch.SearchClient(
        query,
        tbs="li:1",
        max_search_result_urls_to_return=1,
        yagooglesearch_manages_http_429s=False,
        verbosity=0,
        verbose_output=False,
        proxy=LINKEDIN_SCRAPER_PROXY,
    )
    client.assign_random_user_agent()

    urls = client.search()
    if not len(urls):
        raise Exception("Page not found")
    else:
        data = urls[0]
        # Validate this is an actual linkedin url
        # @TODO
        if data == "HTTP_429_DETECTED":
            raise Exception("HTTP_429_DETECTED")
        else:
            return data


class GoogleScrapeWorker(BaseScraperWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def validate_linkedin_url_or_raise(self, input: str):
        """This methods validates that the google extracted data is an actual linkedin company page"""
        if not input.startswith("https://www.linkedin.com/company/"):
            raise ScrapingError(f"Invalid extracted linkeding page: {input}")

    def run_task(self, company_name: str):
        """
        This task will find Linkeding company pages using google.
        :param company_name: A company name
        :return: a valid LinkedIn company page
        """
        # First run the google search query
        result = run_google_query(company_name)

        # make sure is an actual linkedin page
        self.validate_linkedin_url_or_raise(input=result)

        return result
