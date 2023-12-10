import re

from linkedin_scraper.scrapers.base import BaseScraperWorker

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync


class LinkedinScrapeWorker(BaseScraperWorker):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_employee_count_regex(text):
        """
        This method parses the text in the `.top-card-layout__card` html field of Linkedin company page,
        to extract only the employee count number.
        :param text:
        :return:
        """
        text = text.replace("\n", " ")
        employee_re = re.compile(r"(.*) (View all) (.*) (employees)", re.IGNORECASE)
        match = employee_re.match(text)
        if match:
            return int(match.group(3).replace(",", ""))

    def run_task(self, page_url: str) -> int:
        """
        This task will extract the Employee count from the Company linkedin page.
        The value can be extracted from the `.top-card-layout__card` html field, without authentication.
        :param page_url: Linkedin company page
        :return: Employee count
        """
        with sync_playwright() as p:
            browser = p.chromium.launch()

            page = browser.new_page()
            stealth_sync(page)

            page.goto(page_url)

            top_card_element = page.locator(".top-card-layout__card").first

            employee_count = self.get_employee_count_regex(
                top_card_element.inner_text()
            )

            page.close()
            browser.close()

            return employee_count
