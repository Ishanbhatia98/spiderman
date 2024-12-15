from enum import Enum
from urllib.parse import urlparse

from .amazon_in import AmazonInDomainType
from .custom import CustomDomainType
from .flipkart import FlipkartDomainType

default_config = {
    "purchase_button_keywords": [
        "add to cart",
        "add to bag",
        "buy now",
        "add to basket",
    ],
    "search_placeholder_keywords": ["search", "Search", "SEARCH"],
    "max_page_visits_in_iteration": 100,
    "product_page_regex_patterns": [],
    "next_page_button_keywords": ["next"],
}


crawlers = {
    "www.amazon.in": AmazonInDomainType,
    "www.flipkart.com": FlipkartDomainType,
    "custom": CustomDomainType,
}


def get_domain_crawler(domain_config):
    domain_url = domain_config["domain_url"]
    crawler = crawlers["custom"]
    for option in crawlers:
        if option == domain_url or option == urlparse(domain_url).netloc:
            crawler = crawlers[option]
    config = default_config.copy()
    config.update(domain_config)
    return crawler(config)


if __name__ == "__main__":

    domains = [
        "www.amazon.in",
        "https://www.flipkart.com/computers/computer-peripherals/projectors/pr?sid=6bo%2Ctia%2C1hx&fm=neo%2Fmerchandising&iid=M_0cc842bf-96c6-4409-b385-b0a904682f33_2_372UD5BXDFYS_MC.ICU0BSHGNPBF&otracker1=hp_rich_navigation_PINNED_neo%2Fmerchandising_NA_NAV_EXPANDABLE_navigationCard_cc_4_L2_view-all&cid=ICU0BSHGNPBF&p%5B%5D=facets.fulfilled_by%255B%255D%3DFlipkart%2BAssured&p%5B%5D=facets.brand%255B%255D%3DEgate&ctx=eyJjYXJkQ29udGV4dCI6eyJhdHRyaWJ1dGVzIjp7InZhbHVlQ2FsbG91dCI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ2YWx1ZUNhbGxvdXQiLCJpbmZlcmVuY2VUeXBlIjoiVkFMVUVfQ0FMTE9VVCIsInZhbHVlcyI6WyJGcm9tIOKCuTY5OTAiXSwidmFsdWVUeXBlIjoiTVVMVElfVkFMVUVEIn19LCJ0aXRsZSI6eyJtdWx0aVZhbHVlZEF0dHJpYnV0ZSI6eyJrZXkiOiJ0aXRsZSIsImluZmVyZW5jZVR5cGUiOiJUSVRMRSIsInZhbHVlcyI6WyJQcm9qZWN0b3IiXSwidmFsdWVUeXBlIjoiTVVMVElfVkFMVUVEIn19LCJoZXJvUGlkIjp7InNpbmdsZVZhbHVlQXR0cmlidXRlIjp7ImtleSI6Imhlcm9QaWQiLCJpbmZlcmVuY2VUeXBlIjoiUElEIiwidmFsdWUiOiJQUk9FSEhINlVQWk5UUDVEIiwidmFsdWVUeXBlIjoiU0lOR0xFX1ZBTFVFRCJ9fX19fQ%3D%3D",
        "https://www.ajio.com/",
    ]

    for domain in domains:
        crawler = get_domain_crawler({"domain_url": domain})
        print(domain, crawler._platform)
