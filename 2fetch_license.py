import csv
import requests
from concurrent.futures import ThreadPoolExecutor
import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("license.log"),
        logging.StreamHandler()
    ]
)

EMAIL = "planto73@harkenpretty.com"
# start_pos = 0
# end_pos = 20000
MAX_RETRIES = 3
BACKOFF_FACTOR = 5

def fetch_license(review, email):
    url = f"https://api.unpaywall.org/v2/{review['DOI']}"
    retries = 0
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, params={"email": email}, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors
            data = response.json()
            best_oa_location = data.get("best_oa_location")
            review["url"] = best_oa_location.get("url") if best_oa_location else "No url found"
            review["pdf_url"] = best_oa_location.get("url_for_pdf") if best_oa_location else "No url found"
            review["license"] = best_oa_location.get("license") if best_oa_location else "No license found"
            logging.info(f'{review["url"]}, {review["pdf_url"]}, {review["license"]}')
            return
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 404:
                review["url"] = "404"
                review["pdf_url"] = "404"
                review["license"] = "404"
                logging.info(f'{review["url"]}, {review["pdf_url"]}, {review["license"]}')
                return
            logging.warning(f"Attempt {retries + 1} failed: HTTP error occurred: {http_err}, response: {response.text}")
        except requests.exceptions.ConnectionError as conn_err:
            logging.warning(f"Attempt {retries + 1} failed: Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            logging.warning(f"Attempt {retries + 1} failed: Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            logging.warning(f"Attempt {retries + 1} failed: Request error occurred: {req_err}")
        except ValueError as val_err:
            logging.warning(f"Attempt {retries + 1} failed: Value error occurred: {val_err}")
    review["url"] = "FAILURE"
    review["pdf_url"] = "FAILURE"
    review["license"] = "FAILURE"

def fetch_licenses():
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = []
        for review in reviews:
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
