import unittest

from linkedin_scraper.scrapers.linkedin import LinkedinScrapeWorker


class TestEmployeeCountRegex(unittest.TestCase):
    def test_get_employee_count_regex_happy_path(self):
        input_text = " View all 11 employees"
        result = LinkedinScrapeWorker.get_employee_count_regex(text=input_text)
        self.assertEqual(result, 11)

    def test_get_employee_count_regex_empty_str(self):
        input_text = " "
        result = LinkedinScrapeWorker.get_employee_count_regex(text=input_text)
        self.assertEqual(result, None)
