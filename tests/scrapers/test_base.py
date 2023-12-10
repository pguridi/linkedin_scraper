import time
import unittest

from multiprocessing import Queue, Process

from linkedin_scraper.scrapers.base import BaseScraperWorker


class DummyScraper(BaseScraperWorker):
    """
    Dummy scraper type, for testing `BaseScraperWorker`
    """

    def run_task(self, input_data):
        """This dummy task will reverse the `input_data` string"""
        return input_data[::-1]


class TestBaseScraperWorker(unittest.TestCase):
    def setUp(self):
        self.input_queue = Queue()
        self.results_queue = Queue()
        self.scraper = DummyScraper(
            worker_id=1, input_queue=self.input_queue, results_queue=self.results_queue
        )

        # Start the scraper in thread mode
        self.scraper.run_in_thread()

    def tearDown(self):
        self.input_queue = None
        self.results_queue = None
        self.scraper.stop()
        self.scraper = None

    def test_base_scraper_process_check(self):
        """This test checks for the process handling, making sure there are no zombie processes left"""
        # Make sure the process is alive
        self.assertIsInstance(self.scraper.get_process(), Process)

        # Stop the process
        self.scraper.stop()

        # Make sure the process is not alive anymore.
        self.assertEqual(self.scraper.get_process(), None)

    def test_base_scraper_success_task(self):
        """This test checks for successfull task case, without errors."""
        test_input = "sample_data"
        expected_value = "atad_elpmas"

        self.input_queue.put(("scrape_task", 1, test_input))
        time.sleep(0.5)

        type, task_id, data, status = self.results_queue.get()
        returned_task_input, returned_task_result = data

        self.assertEqual(returned_task_result, expected_value)
        self.assertEqual(status, "success")
        self.assertEqual(returned_task_input, test_input)

    def test_base_scraper_process_failed_task(self):
        """This test checks for the proper task status and error message when the task failed"""
        test_input = 3123612  # In this case, an integer input is expected to fail

        self.input_queue.put(("scrape_task", 1, test_input))

        time.sleep(1)

        type, task_id, data, status = self.results_queue.get()
        returned_task_input, returned_task_result = data

        self.assertEqual(returned_task_input, test_input)
        self.assertEqual(
            returned_task_result, "scrape_error: 'int' object is not subscriptable"
        )
        self.assertEqual(status, "failed")

        # Make sure the results queue is empty
        self.assertEqual(self.results_queue.empty(), True)
