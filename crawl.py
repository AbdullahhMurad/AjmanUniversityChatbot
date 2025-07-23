# crawl.py - Optimized Version
import concurrent
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import os
import re
from concurrent.futures import ThreadPoolExecutor

START_URLS = [
    "https://www.ajman.ac.ae/en/prospective-students",
    "https://www.ajman.ac.ae/en/admissions",
    # Add other key URLs
]

def sanitize_filename(url):
    """Convert URL to safe filename"""
    return re.sub(r'[^\w-]', '_', url)[:150] + ".txt"

def fetch_page(url):
    try:
        resp = requests.get(url, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
        resp.raise_for_status()
        return url, resp.text
    except Exception as e:
        print(f"⚠️ Failed {url}: {str(e)[:100]}")
        return None

def extract_main_content(soup):
    # Remove unwanted elements
    for elem in soup(['script', 'style', 'nav', 'footer', 'iframe']):
        elem.decompose()
    return soup.get_text(separator='\n', strip=True)

def crawl_site(start_urls=START_URLS, max_workers=5, out_dir="ajman_crawl"):
    os.makedirs(out_dir, exist_ok=True)
    visited = set()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_page, url): url for url in start_urls}
        
        while futures:
            done, _ = concurrent.futures.wait(futures, return_when=concurrent.futures.FIRST_COMPLETED)
            
            for future in done:
                url = futures.pop(future)
                result = future.result()
                if not result:
                    continue
                
                url, html = result
                soup = BeautifulSoup(html, 'lxml')
                text = extract_main_content(soup)
                
                # Save to individual file
                filename = sanitize_filename(url)
                with open(os.path.join(out_dir, filename), 'w', encoding='utf-8') as f:
                    f.write(f"URL: {url}\nCONTENT:\n{text}")
                
                print(f"✅ Saved: {filename}")
                visited.add(url)
                
                # Find new links (with depth control)
                if len(visited) < 50:  # Limit total pages
                    for link in soup.find_all('a', href=True):
                        new_url = urljoin(url, link['href'])
                        if (urlparse(new_url).netloc == urlparse(url).netloc 
                            and new_url not in visited):
                            futures[executor.submit(fetch_page, new_url)] = new_url

if __name__ == "__main__":
    crawl_site()

# import requests
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin, urlparse
# import time
# import os

# START_URLS = [
#     "https://www.ajman.ac.ae/",
#     "https://www.ajman.ac.ae/en/prospective-students",
#     "https://www.ajman.ac.ae/en/current-students",
#     "https://www.ajman.ac.ae/en/faculty-and-staff",
#     "https://alumni.ajman.ac.ae/",
#     "https://library.ajman.ac.ae/",
#     "https://live.ajman.ac.ae/aujobs/",
#     "https://giving.ajman.ac.ae/",
#     "https://www.ajman.ac.ae/en/blog",
#     "https://www.ajman.ac.ae/en/directory",
# ]

# def get_domain(url):
#     return urlparse(url).netloc

# def get_all_links(url, domain):
#     try:
#         resp = requests.get(url, timeout=10)
#         soup = BeautifulSoup(resp.text, 'html.parser')
#         links = set()
#         for a in soup.find_all('a', href=True):
#             joined = urljoin(url, a['href'])
#             parsed = urlparse(joined)
#             # Only follow links within the same domain and scheme
#             if parsed.netloc == domain and parsed.scheme.startswith("http"):
#                 clean_url = parsed.scheme + "://" + parsed.netloc + parsed.path.rstrip('/')
#                 links.add(clean_url)
#         return links
#     except Exception as e:
#         print(f"Failed to get links from {url}: {e}")
#         return set()

# def get_visible_text(soup):
#     for script in soup(["script", "style", "noscript"]):
#         script.extract()
#     text = soup.get_text(separator="\n", strip=True)
#     # remove excessive blank lines
#     lines = [line.strip() for line in text.splitlines()]
#     return "\n".join(line for line in lines if line)

# def crawl_site(start_url, max_pages=40, out_dir="ajman_crawl"):
#     domain = get_domain(start_url)
#     visited = set()
#     to_visit = set([start_url])
#     all_text = []
#     os.makedirs(out_dir, exist_ok=True)
#     page_count = 0

#     while to_visit and len(visited) < max_pages:
#         url = to_visit.pop()
#         if url in visited:
#             continue
#         print(f"Visiting: {url}")
#         try:
#             resp = requests.get(url, timeout=10)
#             soup = BeautifulSoup(resp.text, 'html.parser')
#             page_text = get_visible_text(soup)
#             all_text.append(f"URL: {url}\n{page_text}\n")
#             links = get_all_links(url, domain)
#             to_visit |= (links - visited)
#         except Exception as e:
#             print(f"Error fetching {url}: {e}")
#         visited.add(url)
#         page_count += 1
#         time.sleep(1)  # polite crawling

#     out_path = os.path.join(out_dir, f"{domain.replace('.', '_')}_crawl.txt")
#     with open(out_path, "w", encoding="utf-8") as f:
#         for page in all_text:
#             f.write(page + "\n\n" + "="*80 + "\n\n")
#     print(f"Saved {len(all_text)} pages to {out_path}")

# if __name__ == "__main__":
#     for url in START_URLS:
#         crawl_site(url, max_pages=40)