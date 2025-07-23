import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

visited = set()
output_dir = "crawl"

# Ensure output folder exists
os.makedirs(output_dir, exist_ok=True)

def is_internal_link(link, base_netloc):
    """Check if a link is internal (same domain or relative)."""
    parsed = urlparse(link)
    return parsed.netloc == '' or parsed.netloc == base_netloc

def safe_filename_from_url(url):
    """Generate a safe filename from a URL."""
    parsed = urlparse(url)
    path = parsed.netloc + parsed.path
    clean = path.replace("/", "_").replace(":", "_").strip("_")
    if not clean:
        clean = "index"
    if len(clean) > 100:
        clean = clean[:100]
    return clean + ".txt"

def crawl(url, base_url, depth=1):
    """Recursive crawler function."""
    if url in visited or depth <= 0:
        return

    print(f"\n🔗 Crawling: {url}")
    visited.add(url)

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text(separator='\n', strip=True)

        # Save content to file in /crawl/
        filename = safe_filename_from_url(url)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)

        # Preview first few lines
        print(f"\n📄 Preview of {filename}:\n")
        print('\n'.join(text.split('\n')[:20]))

        # Recursively crawl internal links
        base_netloc = urlparse(base_url).netloc
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()

            # Skip non-web links
            if not href.startswith(('http://', 'https://', '/')):
                continue

            # Construct absolute URL
            full_link = urljoin(base_url, href)

            # Only crawl internal links
            if is_internal_link(full_link, base_netloc):
                crawl(full_link, base_url, depth=depth - 1)

        time.sleep(1)  # Be polite

    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")

if __name__ == "__main__":
    start_url = input("Enter a base URL to crawl: ").strip()
    print("\n🚀 Starting crawler...\n")
    crawl(start_url, start_url, depth=2)



# import os
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import time

# visited = set()
# output_dir = "crawl"

# # Create the folder if it doesn't exist
# os.makedirs(output_dir, exist_ok=True)

# def is_internal_link(link, base_netloc):
#     parsed = urlparse(link)
#     return parsed.netloc == '' or parsed.netloc == base_netloc

# def safe_filename_from_url(url):
#     clean_name = url.replace("https://", "").replace("http://", "").replace("/", "_")
#     if len(clean_name) > 100:
#         clean_name = clean_name[:100]  # Truncate long names
#     return clean_name + ".txt"

# def crawl(url, base_url, depth=1):
#     if url in visited or depth <= 0:
#         return

#     print(f"\n🔗 Crawling: {url}")
#     visited.add(url)

#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         }
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')
#         text = soup.get_text(separator='\n', strip=True)

#         print(f"\n📄 Text Preview from {url}:\n")
#         print('\n'.join(text.split('\n')[:20]))  # First 20 lines

#         # Save text file in crawl/ subdirectory
#         filename = safe_filename_from_url(url)
#         filepath = os.path.join(output_dir, filename)

#         with open(filepath, "w", encoding="utf-8") as f:
#             f.write(text)

#         # Recursively crawl internal links
#         for a_tag in soup.find_all('a', href=True):
#             link = urljoin(base_url, a_tag['href'])
#             if is_internal_link(link, urlparse(base_url).netloc):
#                 crawl(link, base_url, depth=depth-1)

#         time.sleep(1)  # Avoid overloading server

#     except requests.RequestException as e:
#         print(f"❌ Error fetching {url}: {e}")

# if __name__ == "__main__":
#     start_url = input("Enter a base URL to crawl: ").strip()
#     print("Starting crawler...\n")
#     crawl(start_url, start_url, depth=2)



# import requests
# from bs4 import BeautifulSoup

# def crawl_and_extract_text(url):
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
#         }
#         print("Fetching URL...")
#         response = requests.get(url, headers=headers, timeout=10)
#         response.raise_for_status()

#         soup = BeautifulSoup(response.text, 'html.parser')
#         text = soup.get_text(separator='\n', strip=True)

#         with open("output.txt", "w", encoding="utf-8") as f:
#             f.write(text)

#         print("\n--- Extracted Preview ---\n")
#         print('\n'.join(text.split('\n')[:30]))  # First 30 lines

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching the URL: {e}")

# if __name__ == "__main__":
#     url = input("Enter a URL to crawl: ")
#     crawl_and_extract_text(url)





# import requests
# from bs4 import BeautifulSoup

# def crawl_and_extract_text(url):
#     try:
#         # Send HTTP request
#         response = requests.get(url)
#         response.raise_for_status()  # Raise error for bad status

#         # Parse HTML content
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Extract and clean all text
#         text = soup.get_text(separator='\n', strip=True)

#         # Store to file (optional)
#         with open("output.txt", "w", encoding="utf-8") as file:
#             file.write(text)

#         # Print to terminal
#         print("\n--- Extracted Text ---\n")
#         print(text)

#     except requests.exceptions.RequestException as e:
#         print(f"Error fetching the URL: {e}")

# if __name__ == "__main__":
#     target_url = input("Enter a URL to crawl: ")
#     crawl_and_extract_text(target_url)



# import fitz

# def extract_blocks(pdf_path, page_num):
#     doc = fitz.open(pdf_path)
#     page = doc.load_page(page_num)
#     blocks = page.get_text("blocks")
#     for i, block in enumerate(blocks):
#         print(f"\n--- Block {i+1} ---\n{block[4]}")
#     doc.close()

# extract_blocks("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf", page_num=1)
 

# import fitz  # PyMuPDF

# def extract_text_from_pdf(pdf_path):
#     doc = fitz.open(pdf_path)
#     all_text = ""
#     for page in doc:
#         text = page.get_text("text")  # "text" mode gets all text on the page
#         all_text += text + "\n"
#     doc.close()
#     return all_text

# print(extract_text_from_pdf("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf"))




# import pdfplumber

# with pdfplumber.open("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf") as pdf:
#     text = ""
#     for page in pdf.pages:
#         page_text = page.extract_text()
#         if page_text:
#             text += page_text + "\n"
# print(text)



# from pdf2image import convert_from_path
# import pytesseract

# pages = convert_from_path('C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf')
# all_text = ""
# for page in pages:
#     all_text += pytesseract.image_to_string(page)
# print(all_text)



# import pdfplumber

# with pdfplumber.open("") as pdf:
#     text = ""
#     for page in pdf.pages:
#         text += page.extract_text() + "\n"
# print(text)



# from langchain_huggingface import HuggingFaceEmbeddings

# embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
# result = embedding.embed_query("This is a test.")
# print(result[:5])



# from langchain.docstore.document import Document
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import FAISS

# documents = [Document(page_content="Hello world"), Document(page_content="This is another doc")]
# embeddings = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
# store = FAISS.from_documents(documents, embedding=embeddings)
# print("✅ FAISS store created")





# FAILED

# from langchain_huggingface import HuggingFaceEmbeddings

# embedding = HuggingFaceEmbeddings(model_name="hkunlp/instructor-xl")
# result = embedding.embed_query("This is a test.")
# print(result[:5])

# from langchain_community.document_loaders import PyMuPDFLoader

# loader = PyMuPDFLoader("C:/Users/kinga/Downloads/PymufTest/PDFs/NewStudentFAQs.pdf")
# docs = loader.load()
# print(len(docs))