import requests
from bs4 import BeautifulSoup
import re
import time

def get_pmc_html(pmid, max_retries=3, delay=1):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } # Avoid 403

    # PMCID from PMID
    efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id={pmid}&retmode=xml"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(efetch_url, headers=headers)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise ConnectionError(f"Failed to fetch data for PMID {pmid} after {max_retries} attempts: {str(e)}")
            time.sleep(delay)

    soup = BeautifulSoup(response.content, 'xml')
    
    pmc_id = soup.find('ArticleId', IdType="pmc")
    if not pmc_id:
        raise ValueError(f"No PMC ID found for PMID {pmid}")
    
    pmc_id = pmc_id.text
    
    # fetch the HTML content
    pmc_url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmc_id}/"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(pmc_url, headers=headers)
            response.raise_for_status()
            break
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise ConnectionError(f"Failed to fetch HTML for PMC ID {pmc_id} after {max_retries} attempts: {str(e)}")
            time.sleep(delay)
    
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('div', class_='jig-ncbiinpagenav')
    
    if not main_content:
        raise ValueError(f"Could not find main content for PMC ID {pmc_id}")
    
    return main_content

def get_refs(html_soup):
    refs = []
    ref_list = html_soup.find('div', id='reference-list')
    
    if ref_list:
        ref_items = ref_list.find_all('div', class_='ref-cit-blk')
        for item in ref_items:
            ref_text = item.get_text(strip=True)
            refs.append(ref_text)
    else:
        print("No reference list found with id 'reference-list'")
    
    return refs

pmid = "34918032"
try:
    html = get_pmc_html(pmid)
    refs = get_refs(html)

except (ValueError, ConnectionError) as e:
    print(f"Error: {str(e)}")