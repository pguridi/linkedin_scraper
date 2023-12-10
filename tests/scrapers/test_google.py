import mock
import unittest

from linkedin_scraper.scrapers.google import GoogleScrapeWorker
from linkedin_scraper.exceptions import ScrapingError


class TestGoogleScrapeWorker(unittest.TestCase):
    @mock.patch("linkedin_scraper.scrapers.google.run_google_query")
    def test_google_extract_validation(self, run_google_query):
        run_google_query.return_value = "https://www.microsoft.com"
        input_text = "Microsoft"

        # no real queues neeed for this test
        google_worker = GoogleScrapeWorker(
            worker_id=1, input_queue=None, results_queue=None
        )

        # validates that the validation exception is being raised
        with self.assertRaises(ScrapingError) as cm:
            google_worker.run_task(input_text)

        self.assertEqual(
            str(cm.exception),
            "Invalid extracted linkeding page: https://www.microsoft.com",
        )
