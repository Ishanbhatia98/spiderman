import re
import time

from .base import BaseDomainType, load_cache, save_to_cache


class CustomDomainType(BaseDomainType):
    _platform = "unknown"

    def __init__(self, config):
        self.config = config
        self.domain_url = config["domain_url"]
        self.cache = load_cache(self.domain_url)
        self.driver = super()._get_driver()

    @classmethod
    def match_product_url(cls, url):
        pattern = re.compile(r"/product/|/p/|/item/")
        if pattern.search(url):
            return True
        return False

    def is_product_url(self, url_to_check) -> bool:
        if url_to_check in self.cache["product"]:
            return True
        if url_to_check in self.cache["other"]:
            return False

        patterns = self.config.get("product_page_regex_patterns", [])
        for pat in patterns:
            try:
                regex = re.compile(pat)
            except re.error as e:
                # Handle invalid regex pattern
                print(f"Invalid regex pattern '{pat}' skipped. Error: {e}")
                continue

            if regex.search(url_to_check):
                return True

        return super()._is_product_url(
            self.cache, self.config, url_to_check, self.driver
        )

    def extract_urls_from_page(self, mxc=10**9):
        product_urls, to_check = super()._extract_urls_from_page(
            self.cache, self.config, self.driver, mxc
        )
        visit_count, other = 0, set()
        while to_check:
            if mxc <= 0:
                break
            mxc -= 1
            visit_count += 1
            url = to_check.pop()
            print(f" {visit_count} Checking url: ", url)
            time.sleep(1)
            if self.is_product_url(url):
                product_urls.add(url)
            else:
                other.add(url)
        self.cache = save_to_cache(self.domain_url, product_urls, other, self.cache)
        return product_urls, other, visit_count

    def find_search_input(self):
        return super()._find_search_input(self.config, self.driver)

    def search_domain(self, query):
        search_input_element = self.find_search_input()
        if not search_input_element:
            return False
        try:
            search_input_element.clear()
            search_input_element.send_keys(query)
            search_input_element.submit()
            time.sleep(3)
            return True
        except Exception as e:
            print(
                f"Error searching for query:{query}, on url:{self.driver.current_url}, with error:{e}"
            )
            return False

    def find_next_page_button(self):
        return super()._find_next_page_button(self.config, self.driver)

    def find_and_click_next_page_button(self):
        btn = self.find_next_page_button()
        if not btn:
            return False
        try:
            btn.click()
            time.sleep(2)
            return True
        except Exception as e:
            print(
                f"Error clicking next page button for url:{self.driver.current_url} with error: {e}"
            )
            return False

    def run(self, max_page_visits=100):
        start_time = time.time()
        visited = set()
        self.driver.get(self.config["domain_url"])
        visited.add(self.driver.current_url)
        print("on page: ", self.driver.current_url)
        product_urls, other, visit_count = self.extract_urls_from_page(max_page_visits)
        max_page_visits -= visit_count
        while max_page_visits > 0 and other:
            url = other.pop()
            if url in visited:
                continue
            print("on page: ", url)
            self.driver.get(url)
            visited.add(self.driver.current_url)
            curr_product_urls, other_urls, visit_count = self.extract_urls_from_page(
                max_page_visits
            )
            max_page_visits -= visit_count
            product_urls = product_urls.union(curr_product_urls)
            other = other.union(other_urls)
            while max_page_visits > 0:
                self.driver, flag = self.find_and_click_next_page_button()
                if self.driver.current_url in visited or flag == False:
                    break
                visited.add(self.driver.current_url)
                max_page_visits -= 1
                curr_product_urls, other_urls, visit_count = (
                    self.extract_urls_from_page(max_page_visits)
                )
                max_page_visits -= visit_count
                product_urls = product_urls.union(curr_product_urls)
                other = other.union(other_urls)
            max_page_visits -= 1
        print("time taken ", time.time() - start_time)
        return product_urls, other


if __name__ == "__main__":
    config = {
        "purchase_button_keywords": [
            "add to cart",
            "add to bag",
            "buy now",
            "add to basket",
        ],
        "search_placeholder_keywords": ["search", "Search", "SEARCH"],
        "max_page_visits_in_iteration": 100,
        "domain_url": "https://www.amazon.in",
        "product_page_regex_patterns": ["/p/", "/item/"],
    }
    custom_dt = CustomDomainType(config)
    ps, os = custom_dt.run()
    print("Product urls")
    for p in ps:
        print(p)

    print("Other urls")
    for o in os:
        print(o)
