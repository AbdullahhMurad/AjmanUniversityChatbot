import os
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_internal_link(link, base_netloc):
    parsed = urlparse(link)
    return parsed.netloc == '' or parsed.netloc == base_netloc

def safe_filename_from_url(url):
    parsed = urlparse(url)
    path = parsed.netloc + parsed.path
    clean = path.replace("/", "_").replace(":", "_").strip("_")
    if not clean:
        clean = "index"
    if len(clean) > 100:
        clean = clean[:100]
    return clean + ".txt"

def crawl(url, base_url, output_dir, visited, depth=1):
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
        filename = safe_filename_from_url(url)
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"\n📄 Preview of {filename}:\n")
        print('\n'.join(text.split('\n')[:20]))
        base_netloc = urlparse(base_url).netloc
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href.startswith(('http://', 'https://', '/')):
                continue
            full_link = urljoin(base_url, href)
            if is_internal_link(full_link, base_netloc):
                crawl(full_link, base_url, output_dir, visited, depth=depth - 1)
        time.sleep(1)
    except requests.RequestException as e:
        print(f"❌ Error fetching {url}: {e}")

def run_crawler(start_url, depth=2, output_dir="crawl"):
    visited = set()
    os.makedirs(output_dir, exist_ok=True)
    crawl(start_url, start_url, output_dir, visited, depth=depth)

if __name__ == "__main__":
    start_url = input("Enter a base URL to crawl: ").strip()
    print("\n🚀 Starting crawler...\n")
    run_crawler(start_url, depth=2)



# import os
# import time
# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse

# visited = set()
# output_dir = "crawl"

# # Ensure output folder exists
# os.makedirs(output_dir, exist_ok=True)

# def is_internal_link(link, base_netloc):
#     """Check if a link is internal (same domain or relative)."""
#     parsed = urlparse(link)
#     return parsed.netloc == '' or parsed.netloc == base_netloc

# def safe_filename_from_url(url):
#     """Generate a safe filename from a URL."""
#     parsed = urlparse(url)
#     path = parsed.netloc + parsed.path
#     clean = path.replace("/", "_").replace(":", "_").strip("_")
#     if not clean:
#         clean = "index"
#     if len(clean) > 100:
#         clean = clean[:100]
#     return clean + ".txt"

# def crawl(url, base_url, depth=1):
#     """Recursive crawler function."""
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

#         # Save content to file in /crawl/
#         filename = safe_filename_from_url(url)
#         filepath = os.path.join(output_dir, filename)
#         with open(filepath, "w", encoding="utf-8") as f:
#             f.write(text)

#         # Preview first few lines
#         print(f"\n📄 Preview of {filename}:\n")
#         print('\n'.join(text.split('\n')[:20]))

#         # Recursively crawl internal links
#         base_netloc = urlparse(base_url).netloc
#         for a_tag in soup.find_all('a', href=True):
#             href = a_tag['href'].strip()

#             # Skip non-web links
#             if not href.startswith(('http://', 'https://', '/')):
#                 continue

#             # Construct absolute URL
#             full_link = urljoin(base_url, href)

#             # Only crawl internal links
#             if is_internal_link(full_link, base_netloc):
#                 crawl(full_link, base_url, depth=depth - 1)

#         time.sleep(1)  # Be polite

#     except requests.RequestException as e:
#         print(f"❌ Error fetching {url}: {e}")

# if __name__ == "__main__":
#     start_url = input("Enter a base URL to crawl: ").strip()
#     print("\n🚀 Starting crawler...\n")
#     crawl(start_url, start_url, depth=2)
