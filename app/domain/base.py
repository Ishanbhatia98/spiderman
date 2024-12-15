import json
import os
import time
from collections import defaultdict
from urllib.parse import urljoin, urlparse

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def load_cache(domain_url, cache=None):
    domain_key = domain_url.replace(".", "_")
    cache = cache or defaultdict(lambda: set())
    product_url_cache_file = f"cache/{domain_key}__product.txt"
    if os.path.exists(product_url_cache_file):
        with open(product_url_cache_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                cache["product"].add(line.strip())

    other_url_cache_file = f"cache/{domain_key}__other.txt"
    if os.path.exists(other_url_cache_file):
        with open(other_url_cache_file, "r", encoding="utf-8") as f:
            for line in f.readlines():
                cache["product"].add(line.strip())
    return cache


def save_to_cache(domain_url, product_urls, other_urls, cache=None):
    # Ensure cache directory
    os.makedirs("cache", exist_ok=True)

    # Extract just the domain (host) part of the URL to avoid invalid characters
    parsed_url = urlparse(domain_url)
    domain = parsed_url.netloc  # e.g., "www.amazon.in"
    domain_key = domain.replace(".", "_")  # "www_amazon_in"

    # Load or use provided cache
    cache = cache or load_cache(domain_url)

    # Assuming product_urls and other_urls are sets
    product_urls = set(product_urls) - cache["product"]
    other_urls = set(other_urls) - cache["other"]

    product_url_cache_file = f"cache/{domain_key}__product.txt"
    other_url_cache_file = f"cache/{domain_key}__other.txt"

    # Append new product URLs
    with open(product_url_cache_file, "a+", encoding="utf-8") as f:
        for purl in product_urls:
            purl = purl.strip()
            cache["product"].add(purl)
            f.write(purl + "\n")

    # Append new other URLs
    with open(other_url_cache_file, "a+", encoding="utf-8") as f:
        for ourl in other_urls:
            ourl = ourl.strip()
            cache["other"].add(ourl)
            f.write(ourl + "\n")

    return cache


class BaseDomainType:
    @classmethod
    def match_product_url(cls, url):
        raise NotImplementedError()

    @classmethod
    def _is_product_url(cls, cache, config, url_to_check, driver) -> bool:
        try:
            driver.get(url_to_check)
            current_url = driver.current_url
            # finding elements in screen because the add to bag button is definitely on screen on the top of the product page
            elements = driver.execute_script(
                """
                return Array.from(
                    document.querySelectorAll("button, input[type='submit'], a, div")
                ).filter(el => {
                    // Check basic display visibility
                    const style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility === 'hidden') {
                        return false;
                    }
                    const rect = el.getBoundingClientRect();
                    return (
                        rect.top >= 0 && 
                        rect.left >= 0 && 
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                });
            """
            )
            match_count = {kw: 0 for kw in config["purchase_button_keywords"]}
            for el in elements:
                try:
                    text = (el.get_attribute("value") or el.text or "").strip().lower()
                except StaleElementReferenceException:
                    continue
                if not text or len(text) > 20:
                    continue
                for kw in config["purchase_button_keywords"]:
                    if kw in text:
                        match_count[kw] += 1
            return any(v > 0 for v in match_count.values())
        except Exception as e:
            print(
                f"Error verifying url: {driver.current_url} as product page with error: {e}"
            )
            return False

    @classmethod
    def _get_anchor_elements(cls, driver):
        elems = driver.find_elements(By.TAG_NAME, "a")
        if True:
            elems += driver.execute_script(
                """
                function getAllAnchors(root) {
                    const anchors = [];
                    // Collect all anchors in the current root
                    anchors.push(...root.querySelectorAll('a'));

                    // Check for shadow roots in all elements
                    const allElems = root.querySelectorAll('*');
                    for (let el of allElems) {
                        if (el.shadowRoot) {
                            anchors.push(...getAllAnchors(el.shadowRoot));
                        }
                    }
                    return anchors;
                }

                return getAllAnchors(document);
            """
            )
        return elems

    @classmethod
    def _extract_urls_from_page(cls, cache, config, driver, mxc=10**9):
        product_url, to_check = set(), set()
        try:
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "a")))
            elems = cls._get_anchor_elements(driver)
            for e in elems:
                href = e.get_attribute("href")
                if isinstance(href, str) and not href.startswith("http"):
                    href = urljoin(config["domain_url"], href)
                if href and href.startswith(config["domain_url"]):
                    if cls.match_product_url(href):
                        product_url.add(href)
                    else:
                        to_check.add(href)
            print(f"Total urls to check on page: {driver.current_url}: ", len(to_check))
            print(
                f"Total product urls matched on page: {driver.current_url}: ",
                len(to_check),
            )
            return product_url, to_check
        except Exception as e:
            print(
                f"Error extracting links from page:{driver.current_url} with error: {e}"
            )
            return set(), set()

    @classmethod
    def _find_search_input(cls, config, driver):
        try:
            inputs = driver.find_elements(By.TAG_NAME, "input")
            for inp in inputs:
                t = (inp.get_attribute("type") or "").lower()
                ph = (inp.get_attribute("placeholder") or "").lower()
                name = (inp.get_attribute("name") or "").lower()

                if (
                    t in ["text", "search"] or name in ["q", "search", "field-keywords"]
                ) and any(
                    k.lower() in ph for k in config["search_placeholder_keywords"] if ph
                ):
                    return inp

                if any(k in ph for k in cls.config["search_placeholder_keywords"]):
                    return inp
        except Exception as e:
            print(
                f"Error finding search bar for url:{driver.current_url} with error: {e}"
            )
        return None

    @classmethod
    def _search_domain(cls, config, driver, query):
        try:
            search_input_element = cls.find_search_input(config, driver)
            search_input_element.clear()
            search_input_element.send_keys(query)
            search_input_element.submit()
            time.sleep(3)
            return driver, True
        except Exception as e:
            print(
                f"Error searching for query:{query}, on url:{driver.current_url}, with error:{e}"
            )
            return driver, False

    @classmethod
    def _find_next_page_button(cls, config, driver):
        try:
            clickable = driver.find_elements(By.XPATH, "//a|//button")
            for c in clickable:
                text = (c.text or "").strip().lower()
                if any(
                    kw in text
                    for kw in config.get("next_page_button_keywords", ["next"])
                ):
                    return c
        except Exception as e:
            print(
                f"Error finding next page button for url:{driver.current_url} with error: {e}"
            )
        return None

    @classmethod
    def _find_and_click_next_page_button(cls, driver):
        btn = cls.find_next_page_button(driver)
        if not btn:
            return driver, False
        try:
            btn.click()
            time.sleep(2)
            return driver, True
        except Exception as e:
            print(
                f"Error clicking next page button for url:{driver.current_url} with error: {e}"
            )
            return driver, False

    @classmethod
    def _get_domain_categories(cls): ...

    @classmethod
    def _get_driver(cls):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-extensions")
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        return driver
