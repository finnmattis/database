import PyPDF2
import requests
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('API_KEY'))

def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def get_sections(pdf):
    response = client.chat.completions.create(model="gpt-4o",
    messages=[
        {"role": "system", "content": "I am going to give you the following systematic review. I want you to return to me the sections where it talks about specific studies included in the review. ONLY give me the (nameOfStudy)<sep>(discussion) and each study should be seperated by <newstudy>"},
        {"role": "user", "content": pdf}
    ])
    response = response.choices[0].message.content
    studies = response.split("<newstudy>")
    sections = {}
    for study in studies:
        study.strip()
        title, content = study.split("<sep>")
        title = title.strip()
        content = content.strip()
        sections[title] = content
    return sections


download_pdf("https://europepmc.org/backend/ptpmcrender.fcgi?accid=PMC7046131&blobtype=pdf", "temp/a.pdf")
pdf_path = 'temp/a.pdf'
text = extract_text_from_pdf(pdf_path)
sections = get_sections(text)
print(sections)
os.remove("temp/a.pdf")