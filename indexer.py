import requests
from queue import Queue, Empty
from time import sleep
from collections import deque
from threading import Thread, current_thread
from multiprocessing import cpu_count
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer


class Indexer:
    scan_queue = Queue()
    results_queue = deque()
    working_threads = {}
    STOP_WORKERS = False

    def __init__(self, max_threads=None):
        self.max_threads = max_threads or cpu_count()

    @property
    def threads_working(self):
        """ Returns True if any of the thread is working, otherwise return False"""
        return any(self.working_threads.values())

    @staticmethod
    def is_dir(url):
        """ Returns True if given url points to a directory, otherwise returns false """
        if url.endswith('/'):
            return True

        filename = url.rsplit('/', 1)[-1]
        return '.' not in filename

    @staticmethod
    def need_to_index(url):
        # extensions = [
        #     '.mp3', '.m4a', '.wav', '.mkv',
        #     '.mp4', '.wmv', '.epub', '.jpg',
        #     '.png', '.avi', '.rar', '.zip',
        #     '.7z',
        # ]
        # filename = url.rsplit('/', 1)[-1]
        #
        # for ext in extensions:
        #     if ext in filename:
        #         return True

        return True

    @staticmethod
    def clean_url(url):
        url = url.rsplit('?', 1)[0]
        url = url.rsplit('#', 1)[0]

        return url

    def extract_urls(self, folder_url):
        with requests.Session() as session:
            html = session.get(folder_url).text
            soup = BeautifulSoup(html, "html.parser", parse_only=SoupStrainer('a'))

            for anchor in soup('a'):
                anchor_url = anchor.get('href')

                if not anchor_url:
                    continue

                if anchor_url.startswith('/'):
                    continue

                anchor_url = urljoin(folder_url, anchor_url)
                anchor_url = self.clean_url(anchor_url)
                if not anchor_url:
                    continue

                if self.need_to_index(anchor_url):
                    yield anchor_url

    def crawl(self, recurse=True):
        """ Crawls the given website and yields the urls """
        while not self.STOP_WORKERS:
            try:
                folder_url = self.scan_queue.get(timeout=0.01)
                print(f'Crawling {folder_url}')
            except Empty:
                continue

            self.working_threads[current_thread().name] = True

            urls = self.extract_urls(folder_url)

            seen = set()
            for url in urls:
                if url in seen or url == folder_url or not url.startswith(folder_url):
                    continue

                if recurse and self.is_dir(url):
                    self.scan_queue.put(url)
                elif not self.is_dir(url):
                    self.results_queue.append(url)
                seen.add(url)

            self.working_threads[current_thread().name] = False

            if self.scan_queue.empty() and not self.threads_working:
                self.STOP_WORKERS = True
                print('Finished!')

    def scan(self, urls):
        for url in urls:
            self.scan_queue.put(url)

        for _ in range(self.max_threads):
            thread = Thread(target=self.crawl)
            thread.start()

        while self.threads_working:
            if self.results_queue:
                yield self.results_queue.popleft()
            else:
                sleep(0.0001)

        while self.results_queue:
            yield self.results_queue.popleft()

    @staticmethod
    def save_stats(output_file):
        extensions = set()
        with open(output_file, 'r') as urls_file:
            with open(f'stats.txt', 'w') as stats_file:
                if not extensions:
                    lines = 0
                    for line in urls_file:
                        file_ext = line.strip().rsplit('.', 1)[-1]
                        extensions.add(file_ext)
                        lines += 1
                    stats_file.write(f'{lines} total link(s)\n')
                    stats_file.write(f'Found these extension(s): {extensions}\n')

                if extensions:
                    urls_file.seek(0)
                    for ext in extensions:
                        count = 0
                        for line in urls_file:
                            line = line.strip()
                            file_ext = line.rsplit('.', 1)[-1]
                            if ext == file_ext:
                                count += 1
                        stats_file.write(f'{ext}: {count} file(s)\n')
                        urls_file.seek(0)

    def save(self, output_file, parsed_urls):
        """ Saves urls to a file on disk """
        with open(output_file, 'w') as file:
            urls_processed = 0
            urls = []

            for url in parsed_urls:
                urls.append(f'{url}\n')
                urls_processed += 1

                if urls_processed >= 100:
                    file.writelines(urls)
                    # Flushing will let you use other program to process
                    # the output file while the indexer is running.
                    # Example filtering results with grep
                    file.flush()
                    urls = []

            # Save any leftovers
            if urls:
                file.writelines(urls)
                file.flush()

        self.save_stats(output_file)
