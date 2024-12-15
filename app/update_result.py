import csv
import os


def sync_results():
    cache_dir = "cache"
    final_file = "final.csv"
    existing_entries = set()
    if os.path.exists(final_file):
        with open(final_file, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    domain_url, url = row[0], row[1]
                    existing_entries.add((domain_url, url))

    with open(final_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for filename in os.listdir(cache_dir):
            if filename.endswith("__product.txt"):
                file_path = os.path.join(cache_dir, filename)
                domain_url = filename.replace("__product.txt", "").replace("_", ".")
                with open(file_path, "r", encoding="utf-8") as pf:
                    for line in pf:
                        url = line.strip()
                        entry = (domain_url, url)
                        if entry not in existing_entries:
                            existing_entries.add(entry)
                            writer.writerow([domain_url, url])


if __name__ == "__main__":
    sync_results()
