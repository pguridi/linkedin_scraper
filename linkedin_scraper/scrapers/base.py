import logging
from multiprocessing import Process, Queue
from queue import Empty

from linkedin_scraper.config import LOGGER_NAME

logger = logging.getLogger(LOGGER_NAME)


class BaseScraperWorker:
    def __init__(self, worker_id: int, input_queue: Queue, results_queue: Queue):
        """
        This is the base Class that defines the interface for the different Scraper workers.
        :param worker_id: Identifier for the worker instance.
        :param input_queue: Queue where the worker will listen for input tasks.
        :param results_queue: Queue for sending the tasks results.
        """
        self._worker_type = self.__class__.__name__
        self._worker_id = worker_id
        self._input_queue: Queue = input_queue
        self._results_queue: Queue = results_queue
        self._process = None

    def get_worker_type(self):
        """Returns the worker class type"""
        return self._worker_type

    def get_process(self):
        """Useful for testing"""
        return self._process

    def run_in_thread(self):
        """
        Starts the worker main loop in a child Thread
        """
        self._process: Process = Process(target=self.run)
        self._process.start()

    def stop(self):
        """
        Gracefully stops the worker child process
        :return:
        """
        logger.debug(f"closing worker {self._worker_id}")
        if self._process:
            self._process.terminate()
            self._process = None

    def submit_task_result(self, task_id: str, data: tuple, status: str = "success"):
        self._results_queue.put((self.get_worker_type(), task_id, data, status))

    def run(self):
        """
        Start the worker main loop, which handles task data input, processing, and results return.
        """
        logger.debug(f"started {self.get_worker_type()} worker {self._worker_id}")
        while True:
            try:
                message, task_id, input_data = self._input_queue.get(
                    block=True, timeout=0.2
                )
            except Empty:
                continue

            logger.debug(f"Got new task: {message}, {input_data}")
            if message == "scrape_task":
                try:
                    data = self.run_task(input_data)
                    self.submit_task_result(
                        task_id=task_id, data=(input_data, data), status="success"
                    )
                except Exception as e:
                    self.submit_task_result(
                        task_id=task_id,
                        data=(input_data, f"scrape_error: {str(e)}"),
                        status="failed",
                    )

    def run_task(self, input_data):
        """To be implemented by the implementor class"""
        raise NotImplementedError
