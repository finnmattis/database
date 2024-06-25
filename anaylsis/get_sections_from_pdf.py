import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from ftplib import FTP
import os
import tarfile

def download_pmid(pmid, destination_folder='temp'):
    os.makedirs(destination_folder, exist_ok=True)
    url = f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmid}"
    try:
        # Parse Pubmed fetch response for FPT link
        response = requests.get(url)
        print(response.text)
        response.raise_for_status()
        root = ET.fromstring(response.text)

        link = root.find('.//link')
        if link is None:
            raise ValueError(f"No link found for PMID: {pmid}")
        ftp_url = link.get('href')
        if not ftp_url:
            raise ValueError(f"No FTP URL found for PMID: {pmid}")

        print(f"Successfully obtained FTP url {ftp_url}")

        # Download using FTP
        parsed_url = urlparse(ftp_url)
        ftp_host = parsed_url.hostname
        ftp_path = parsed_url.path
        filename = os.path.basename(ftp_path)
        
        with FTP(ftp_host) as ftp:
            ftp.login() # anonymous
            
            ftp_dir = os.path.dirname(ftp_path)
            ftp.cwd(ftp_dir)
            local_filename = os.path.join(destination_folder, filename)
            
            with open(local_filename, 'wb') as local_file:
                ftp.retrbinary(f"RETR {filename}", local_file.write)
        
        print(f"Successfully downloaded {filename}")

        # Extract the downloaded file into temp
        with tarfile.open(local_filename, "r:gz") as tar:
            for member in tar.getmembers():
                member.name = os.path.basename(member.name)
                tar.extract(member, path=destination_folder)

        # Remove the empty directory based on local_filename
        dir_name = os.path.splitext(os.path.splitext(os.path.basename(local_filename))[0])[0] # This is weird but removes .tar.gz
        dir_to_remove = os.path.join(destination_folder, dir_name) 
        os.rmdir(dir_to_remove)

        # Remove the compressed file after extraction
        os.remove(local_filename)

        print(f"Successfully extracted contents to {destination_folder}")

    except requests.RequestException as e:
        raise ConnectionError(f"Failed to fetch data for PMID {pmid}: {str(e)}")
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse XML for PMID {pmid}: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"An error occurred while processing PMID {pmid}: {str(e)}")

def get_formats():
    formats_to_check = {'.html', '.pdf', '.docx', '.xml'}
    available_formats = set()

    try:
        for filename in os.listdir('temp'):
            ext = os.path.splitext(filename)[1].lower()
            if ext in formats_to_check:
                available_formats.add(ext[1:])  # Remove leading dot
    except Exception as e:
        print(f"An error occurred while processing PMID {pmid}: {str(e)}")
    
    return list(available_formats)

pmid = "10796091"
try:
    download_pmid(pmid)
    formats = get_formats()
    print(formats)
except (ValueError, ConnectionError, RuntimeError) as e:
    print(f"Error: {str(e)}")