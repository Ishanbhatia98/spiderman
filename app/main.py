import csv
import json
import os
import shutil
import threading

from app.domain import get_domain_crawler

from .update_result import sync_results


def run_crawler_in_thread(domain_config):
    crawler = get_domain_crawler(domain_config)
    crawler.run(domain_config.get("max_page_visits_in_iteration", 100))


def main():
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
        domains = config["domains"]

        threads = []

        for dconf in domains:
            t = threading.Thread(target=run_crawler_in_thread, args=(dconf,))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

    sync_results()


if __name__ == "__main__":
    main()
