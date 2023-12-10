import logging

from typing import Type
from queue import Empty
from multiprocessing import Queue

import tqdm

from linkedin_scraper.scrapers import (
    BaseScraperWorker,
    GoogleScrapeWorker,
    LinkedinScrapeWorker,
)
from linkedin_scraper.utils import read_csv
from linkedin_scraper.config import (
    LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY,
    LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY,
    LINKEDIN_SCRAPER_MAX_GOOGLE_RETRY,
    LOG_LEVEL,
    LOGGER_NAME,
)


logger = logging.getLogger(LOGGER_NAME)


class ScraperController:
    """
    This Class implements the controller functions required to run Scraping session
    with the different supported Scraper workers (GoogleScrapeWorker, LinkedinScrapeWorker)
    """

    def __init__(self, show_progress=True):
        """
        :param show_progress: Boolean flag to, if enabled, display a command line progress bar.
        """
        self._google_scrape_queue = Queue()
        self._linkedin_scrape_queue = Queue()
        self._results_queue = Queue()
        self._workers = []
        self._results_data = {}
        self._google_retry_counts = (
            {}
        )  # this variable holds the count for the google search retries.
        self._pending_tasks = []

        # Progress bar stuff
        if LOG_LEVEL == "DEBUG":
            # No progress bar should be displayed on debug mode
            self._use_progress_bar = False
        else:
            self._use_progress_bar = show_progress

        self._progress_bar = None
        self._progress_bar_count = 0

    def initialize(self):
        """
        This method initializes everything is neeed for the scraping session, such as
        spawning the scraper workers threads.
        """
        self._pending_tasks = []
        self._results_data = {}

        # Spawn the required amount of workers of each type, according to the variables:
        # LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY, LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY

        for worker_id in range(0, LINKEDIN_SCRAPER_GOOGLE_CONCURRENCY):
            self._spawn_worker_thread(
                worker_id=worker_id,
                worker_class=GoogleScrapeWorker,
                input_queue=self._google_scrape_queue,
            )

        for worker_id in range(0, LINKEDIN_SCRAPER_LINKEDIN_CONCURRENCY):
            self._spawn_worker_thread(
                worker_id=worker_id,
                worker_class=LinkedinScrapeWorker,
                input_queue=self._linkedin_scrape_queue,
            )

    def get_workers(self):
        """Useful for testing"""
        return self._workers

    def _spawn_worker_thread(
        self, worker_id: int, worker_class: Type[BaseScraperWorker], input_queue: Queue
    ):
        """
        Spawns the required `worker_class` Worker type and keep track of the instance.
        :param worker_id: Identifier for the worker instance
        :param worker_class: Worker Class to instantiate
        :param input_queue: Queue the worker will use to listen for tasks
        :return: None
        """
        worker = worker_class(
            worker_id=worker_id,
            input_queue=input_queue,
            results_queue=self._results_queue,
        )
        self._workers.append(worker)
        worker.run_in_thread()

    def _init_progress_bar(self, total: int):
        """
        Initialize the command line progress bar
        :param total: Integer of total tasks, considered 100%.
        :return: None
        """
        if self._use_progress_bar:
            self._progress_bar = tqdm.tqdm(total=total)

    def _update_progress_bar(self):
        """
        Refresh the command line progress bar if enabled.
        """
        if self._use_progress_bar:
            self._progress_bar.update(1)

            if self._progress_bar.n == self._progress_bar.total:
                # reached 100 % progress, close the progress bar
                self._progress_bar.close()

    def _close_progress_bar(self):
        """
        Closes the progress bar if present.
        """
        if self._progress_bar:
            self._progress_bar.close()

    def remove_task_from_pending(self, task_id: str):
        """
        Removes the required `task_id` from the pending task list
        :param task_id:
        :return:
        """
        if task_id in self._pending_tasks:
            self._pending_tasks.remove(task_id)

        self._update_progress_bar()

    def set_task_results_data(self, task_id: str, status: str, data: dict = None):
        """
        Sets the result data for the required `task_id`.
        :param task_id:
        :param status:
        :param data:
        :return:
        """
        if task_id not in self._results_data:
            self._results_data[task_id] = {}

        if data:
            self._results_data[task_id].update(data)

        self._results_data[task_id]["status"] = status

    def get_results_data(self) -> dict:
        """
        Returns the Scrape session tasks results
        :return: Dict
        """
        return self._results_data

    def queue_google_scrape(self, task_id: str, input_data: str):
        """
        Queue a GoogleScrapeWorker task.
        :param task_id: Task identifier
        :param input_data: Input for the task.
        :return: None
        """
        self._google_scrape_queue.put(("scrape_task", task_id, input_data))

    def queue_linkedin_scrape(self, task_id: str, input_data: str):
        """
        Queue a LinkedinScrapeWorker task.
        :param task_id: Task identifier
        :param input_data: Input for the task.
        :return: None
        """
        self._linkedin_scrape_queue.put(("scrape_task", task_id, input_data))

    def process_google_scrape_result(self, task_id: str, data: tuple, status: str):
        """
        This method processes the GoogleScrapeWorker.
        :param task_id: An identifier to track each task
        :param data: Data returned from the scraper worker
        :param status: Status of the task, returned from scraper worker
        :return: None
        """
        input_data, linkedin_url = data
        if status == "success":
            logger.debug(f"Got success result: {input_data} {linkedin_url}")
            # Queue the second task, LinkedIn page data extraction
            self.queue_linkedin_scrape(task_id=task_id, input_data=linkedin_url)

            self.set_task_results_data(
                task_id=task_id, status=status, data={"linkedin_url": linkedin_url}
            )
        elif status == "failed":
            # Retry the failed tasks for a maximum of `RETRY_COUNT` times
            retry_count = self._google_retry_counts.get(input_data, 0)
            if retry_count < LINKEDIN_SCRAPER_MAX_GOOGLE_RETRY:
                # bump the retry count and requeue the task
                self._google_retry_counts[input_data] = retry_count + 1
                logger.debug("failed GoogleScrapeWorker task retrying...")
                self.queue_google_scrape(task_id=task_id, input_data=input_data)
            else:
                logger.error(f"GoogleScrapeWorker failure: {task_id} {data}.")
                # Can not be retried, set the task status and remove it from pending tasks
                self.set_task_results_data(task_id=task_id, status=status)

                self.remove_task_from_pending(task_id=task_id)

    def process_linkedin_scrape_result(self, task_id, data, status):
        """
        This method processes the LinkedinScrapeWorker result.
        :param task_id: An identifier to track each task
        :param data: Data returned from the scraper worker
        :param status: Status of the task, returned from scraper worker
        :return: None
        """
        input_data, linkedin_data = data
        if status == "success":
            self.set_task_results_data(
                task_id=task_id, status=status, data={"employee_count": linkedin_data}
            )
            logger.info(f"Successful LinkedIn extraction for: {task_id}")
        elif status == "failed":
            self.set_task_results_data(task_id=task_id, status=status)
            logger.error(f"Failed LinkedIn extraction for: {task_id} {data}")

        self.remove_task_from_pending(task_id=task_id)

    def stop(self):
        """Gracefully stops the scraping session closing the child processes."""
        logger.info("Stopping workers.")
        for worker in self._workers:
            worker.stop()

        self._workers = []
        self._close_progress_bar()

    def scrape(self, company_names_list: list[str]):
        """
        This method starts the scrape tasks.
        :param company_names_list: List of company names
        :return:
        """
        if not len(self._workers):
            self.initialize()

        # make sure there are no duplicates
        company_names_list = list(set(company_names_list))
        self._init_progress_bar(total=len(company_names_list))

        for company_name in company_names_list:
            task_id = company_name  # for task_id we will use the company name
            self.queue_google_scrape(task_id=task_id, input_data=company_name)
            self._pending_tasks.append(task_id)

        while True:
            # This is the controller main loop, the scraping tasks are queued for the workers
            # and this loops waits for the results.
            if not len(self._pending_tasks):
                # If there are no more pending tasks, finish the main loop.
                self.stop()
                break

            try:
                # listen for task results from the scraper workers
                worker_type, task_id, data, status = self._results_queue.get(
                    timeout=0.2
                )
            except Empty:
                continue

            logger.debug(f"Got result: {worker_type, task_id, data, status}")

            if worker_type == "GoogleScrapeWorker":
                self.process_google_scrape_result(
                    task_id=task_id, data=data, status=status
                )
            elif worker_type == "LinkedinScrapeWorker":
                self.process_linkedin_scrape_result(
                    task_id=task_id, data=data, status=status
                )

        return self.get_results_data()
