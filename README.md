# E-Commerce Web Crawler

## Prerequisites
- Python 3.8+
- pip
- venv (virtual environment module)

## Setup Instructions

### 1. Create a Virtual Environment
```bash
# Create a virtual environment
python3 -m venv webcrawler-env

# Activate the virtual environment
# On macOS and Linux:
source webcrawler-env/bin/activate

# On Windows:
webcrawler-env\Scripts\activate
```

### 2. Install Required Packages
```bash
# Ensure you're in the project directory and virtual environment
pip3 install -r requirements.txt
```

## Usage Commands

### Start Crawler
```bash
python3 -m app.main
```
Begins crawling configured e-commerce domains.

### Update Results
```bash
python3 -m app.update_result
```
Synchronizes and appends results from cache.

### Clear Cache
```bash
python3 -m app.clear_cache
```
Removes all cached crawling data.

## Deactivating Virtual Environment
When you're done working on the project:
```bash
deactivate
```

## Configuration

### Config File (`config.json`)

#### Configuration Parameters
- `domain_url` (Required): Base URL of the e-commerce website
- `max_page_visits_in_iteration`: Maximum number of pages to visit in one crawling iteration
- `purchase_button_keywords`: Array of keywords found on product purchase buttons
- `product_page_regex_patterns`: Optional regex patterns to identify product pages

#### Sample Configuration
```json
{
    "domains": [{
        "purchase_button_keywords": [
            "add to cart", 
            "add to bag", 
            "buy now", 
            "add to basket"
        ],
        "search_placeholder_keywords": [
            "search", 
            "Search", 
            "SEARCH"
        ],
        "max_page_visits_in_iteration": 100,
        "product_page_regex_patterns": [],
        "next_page_button_keywords": ["next"],
        "domain_url": "www.amazon.in"
    }]
}
```

## Output

### Results File
- Filename: `final.csv`
- Columns: 
  1. `domain_url`: Website domain
  2. `product_url`: URL of discovered product pages

## Default Behavior
- By default, the crawler will visit 100 pages per domain
- This can be customized using the `max_page_visits_in_iteration` key in the configuration

## Recommended Workflow
1. Create virtual environment
2. Activate environment
3. Install requirements
4. Configure `config.json`
5. Run the crawler
6. Deactivate environment when done

## Notes
- Always activate the virtual environment before working on the project
- Ensure `config.json` is properly configured before running the crawler
- Adjust `purchase_button_keywords` and `product_page_regex_patterns` to match specific e-commerce website structures