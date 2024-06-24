import PyPDF2
import requests
from openai import OpenAI
import os
import tiktoken
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from openai import RateLimitError
import time
import re

MAX_RETRIES = 5
# MODEL = "gpt-3.5-turbo"
MODEL = "gpt-4o"

client = OpenAI(api_key=os.getenv('API_KEY'))

def get_text(path):
    if os.path.exists(path):
        print("Reading pdf from file")
        with open(path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page_num in range(len(reader.pages)):
                page = reader.pages[page_num]
                text += page.extract_text()
    else:
        print("Reading pdf from internet")
        response = requests.get(path)
        pdf_bytes = BytesIO(response.content)
        reader = PyPDF2.PdfReader(pdf_bytes)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def split_text_into_chunks(text, max_tokens):
    print("Splitting into chunks")
    enc = tiktoken.encoding_for_model(MODEL)
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk = enc.decode(chunk_tokens)
        chunks.append(chunk)
    return chunks

def process_chunk(chunk_index_chunk_pair):
    index, chunk = chunk_index_chunk_pair
    print(f"Processing chunk {index+1}")
    for _ in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": "I am going to give you the following systematic review. I want you to return to me the sections where it talks about specific studies included in the review. Please note there may be no discussion of specific studies. In that case, return <null>. Otherwise, ONLY give me the (nameOfStudy)<sep>(discussion) and each study should be separated by <newstudy>"},
                    {"role": "user", "content": chunk}
                ])
            response = response.choices[0].message.content
            if "<null>" in response:
                return {}
            studies = response.split("<newstudy>")
            section = {}
            for study in studies:
                study = study.strip()
                title, content = study.split("<sep>")
                title = title.strip()
                content = content.strip()
                section[title] = content
            print(f"Chunk {index+1} Done!")
            return section
        except RateLimitError as e:
            match = re.search(r'Please try again in ([\d.]+)s', e.message)
            if match:
                retry_time = float(match.group(1)) + 1 # plus one for fun :)
                print(f"Chunk {index+1} Rate Limit! Retry time: {retry_time} seconds")
            else:
                retry_time = 30
                print(f"Chunk {index+1} Rate Limit! Retry time not found in the error message. Defaulting to 30")
            time.sleep(retry_time)

def get_sections(chunks):
    with ThreadPoolExecutor(max_workers=3) as executor:
        index_chunk_pairs = list(enumerate(chunks))
        results = list(executor.map(process_chunk, index_chunk_pairs))
    
    sections = {}
    for result in results:
        sections.update(result)
    return sections

url = "https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7046131&blobtype=pdf" #dict_keys(['(Adachi 1996)', '(Buckley 1996)', '(Di Munno 1989)', '(Dylan 1984)', '(Sambrook 1993)'])

text = get_text(url)
chunks = split_text_into_chunks(text, 15000)
print(f"There are {len(chunks)} chunks to process")
sections = get_sections(chunks)
print(sections.keys())