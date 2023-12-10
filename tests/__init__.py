import unittest
import time

from linkedin_scraper import ScraperController
from linkedin_scraper.scrapers.base import BaseScraperWorker
from linkedin_scraper.config import (
    LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY,
    LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY,
)


class TestBaseScraperController(unittest.TestCase):
    def setUp(self):
        self.scrape_controller = ScraperController(show_progress=False)
        self.scrape_controller.initialize()

    def tearDown(self):
        self.scrape_controller.stop()
        self.scrape_controller = None

    def test_scraper_controller_process_check(self):
        """This test checks for the process handling, making sure there are no zombie processes left"""
        google_workers = []
        linkedin_workers = []
        time.sleep(2)
        worker: BaseScraperWorker
        for worker in self.scrape_controller.get_workers():
            self.assertIsInstance(worker, BaseScraperWorker)

            if worker.get_worker_type() == "GoogleScrapeWorker":
                google_workers.append(worker)
            elif worker.get_worker_type() == "LinkedinScrapeWorker":
                linkedin_workers.append(worker)

        # Make sure we have the correct number of worker instances of each type
        self.assertEqual(len(google_workers), LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY)
        self.assertEqual(len(linkedin_workers), LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY)

        # Stop the process
        self.scrape_controller.stop()

        time.sleep(2)
        # There shouldn't be any process anymore
        self.assertEqual(len(self.scrape_controller.get_workers()), 0)
