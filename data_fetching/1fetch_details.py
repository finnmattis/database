import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler("output.log"),
        logging.StreamHandler()
    ]
)

# get ids: esearch -db pubmed -query "systematic review[Publication Type]" | efetch -format uid > ids.txt

def fetch_pubmed_details(pmids):
    try:
        query = " OR ".join(pmids)
        result = subprocess.run(
            ['bash', '-c', f'esearch -db pubmed -query "{query}" | efetch -format csv'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except Exception as e:
        return f"Error fetching details for PMIDs {', '.join(pmids)}: {str(e)}"

def main():
    try:
        with open('ids.txt', 'r') as file:
            pmids = [line.strip() for line in file.readlines()][139100:]
    except FileNotFoundError:
        print("Error: ids.txt file not found.")
        return

    total = len(pmids)
    if total == 0:
        print("No PMIDs found in ids.txt.")
        return

    chunk_size = 100
    with open('reviews.csv', 'a') as output_file:
        for i in range(0, total, chunk_size):
            chunk = pmids[i:i+chunk_size]
            logging.info(f"Processing chunk {i//chunk_size + 1} of {((total - 1) // chunk_size) + 1}: PMIDs {chunk[0]} to {chunk[-1]}")
            details = fetch_pubmed_details(chunk)
            output_file.write(details)

    print(f"Completed processing {total} PMIDs.")

if __name__ == "__main__":
    main()
