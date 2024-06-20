import csv
import requests
from concurrent.futures import ThreadPoolExecutor
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("license.log"),
        logging.StreamHandler()
    ]
)

EMAIL = "planto73@harkenpretty.com"
start_pos = 0
end_pos = 20000

def fetch_license(review, email):
    url = f"https://api.unpaywall.org/v2/{review['DOI']}"
    
    response = requests.get(url, params={"email": email})
    data = response.json()
    best_oa_location = data.get("best_oa_location")
    review["url"] = best_oa_location.get("url") if best_oa_location else "No url found"
    review["pdf_url"] = best_oa_location.get("url_for_pdf") if best_oa_location else "No url found"
    logging.info(review["pdf_url"])
    review["license"] = best_oa_location.get("license") if best_oa_location else "No license found"

def fetch_licenses():
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for review in reviews[start_pos:end_pos]:
            futures.append(executor.submit(fetch_license, review, EMAIL))

        for future in futures:
            future.result()

with open("reviews.csv", mode="r") as file:
    reader = csv.DictReader(file)
    reviews = [row for row in reader]
fetch_licenses()

with open("reviews.csv", mode="w", newline="") as file:
    fieldnames = ["ID", "Title", "Authors", "Citation", "Author(s)", "Journal", "Year of Publication", "Full Publication Date", "field1", "field2", "DOI", "license", "url", "pdf_url"]
    
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    
    for review in reviews:
        writer.writerow(review)
