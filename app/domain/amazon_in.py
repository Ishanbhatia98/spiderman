import re

from .custom import CustomDomainType


class AmazonInDomainType(CustomDomainType):
    _platform = "amazon india"

    @classmethod
    def match_product_url(cls, url):
        pattern = re.compile(r"/dp/")
        if pattern.search(url):
            return True
        return super().match_product_url(url)

    def is_product_url(self, url_to_check) -> bool:
        if url_to_check in self.cache["product"]:
            return True
        if url_to_check in self.cache["other"]:
            return False
        return super().is_product_url(url_to_check)

    def find_search_input(self):
        return super().find_search_input()

    def find_next_page_button(self):
        return super().find_next_page_button()


if __name__ == "__main__":
    config = {
        "purchase_button_keywords": ["add to cart", "buy now"],
        "search_placeholder_keywords": ["search", "Search", "SEARCH"],
        "max_page_visits_in_iteration": 100,
        "domain_url": "https://www.amazon.in",
    }
    amzon_dt = AmazonInDomainType(config)
    ps, os = amzon_dt.run(50)
    print("Product urls")
    for p in ps:
        print(p)

    print("Other urls")
    for o in os:
        print(o)
