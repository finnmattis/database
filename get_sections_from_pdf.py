import PyPDF2
import requests
from openai import OpenAI
import os
import tiktoken
from io import BytesIO

# split into chunks
# don't do that stupid file shit

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
    enc = tiktoken.encoding_for_model("gpt-4o")
    tokens = enc.encode(text)
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk = enc.decode(chunk_tokens)
        chunks.append(chunk)
    return chunks

def get_sections(chunks):
    sections = {}
    for index, chunk in enumerate(chunks):
        print(f"Processing chunk {index+1}/{len(chunks)}")
        response = client.chat.completions.create(model="gpt-4o",
        messages=[
            {"role": "system", "content": "I am going to give you the following systematic review. I want you to return to me the sections where it talks about specific studies included in the review. Please note there may be no discussion of specific studies. In that case, return <null>. Otherwise, ONLY give me the (nameOfStudy)<sep>(discussion) and each study should be seperated by <newstudy>"},
            {"role": "user", "content": chunk}
        ])
        response = response.choices[0].message.content
        if "<null>" in response:
            continue
        studies = response.split("<newstudy>")
        for study in studies:
            study.strip()
            title, content = study.split("<sep>")
            title = title.strip()
            content = content.strip()
            sections[title] = content
    return sections

old_url = "https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7046131&blobtype=pdf"
big_url = "https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD013534.pub3/epdf/full"

text = get_text(old_url)
chunks = split_text_into_chunks(text, 25000) # 30,000 limit for my org but putting 30,0000 makes it go over a bit
print(len(chunks))
sections = get_sections(chunks)
print(sections.keys())