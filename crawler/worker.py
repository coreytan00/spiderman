from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        super().__init__(daemon=True)
        
    def run(self):
        start_time = time.time()
        mem = set() #memory cache of unique urls
        robot_cache_a = set() #memory cache of allowed urls
        robot_cache_d = set() #memory cache of disallowed urls
        robot_url_cache = set() #memory cache of crawled robots.txt
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                break
            resp = download(tbd_url, self.config, self.logger)
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper(self.config, robot_cache_a, robot_cache_d, 
                robot_url_cache, mem, tbd_url, resp)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)
            time.sleep(self.config.time_delay)
        print("Number of unique urls: ", len(mem))
        print("My program took", time.time() - start_time, "seconds to run")
        print("All unique urls: ", mem)
