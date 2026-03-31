import requests
from bs4 import BeautifulSoup
import re
import difflib

def discover_urls(page_url: str, soup: BeautifulSoup) -> list[str]:
    """Collect absolute same-origin URLs from anchors (fragments stripped)."""
    seen: set[str] = set()
    out: list[str] = []
    links = soup.find_all('a', attrs={'href': re.compile("")})
    urls = []
    for link in links:
        # display the actual urls
        if link not in urls and link != page_url:
            urls.append(link.get('href'))
    return urls

def download_page(url: str, timeout: int):
    
    # Get page
    try:
        page = requests.get(url=url, timeout=timeout)
        page.raise_for_status()
        html = page.text
    except Exception:
        return "", []
    
    soup = BeautifulSoup(html, "html.parser")
    # Clean up html
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    
    return soup
    
def create_dataset(base_url: str, this_url: str, timeout: int = 15):
    print(f"Crawling: {this_url}")
    dataset = []
    sub_url = ""
    if base_url != this_url:
        sub_url = this_url.replace(base_url, "")
    soup = download_page(base_url, timeout)
    urls = discover_urls(base_url, soup)
    for url in urls:
        create_dataset(base_url,url,timeout)

if __name__ == "__main__":
    url =  "https://www.th-owl.de/skim/dokumentation/"
    soup = download_page(url = url, timeout=15)
    print(soup)
    urls = discover_urls(url, soup)
    with open("output.html", "w", encoding = 'utf-8') as file:
        # prettify the soup object and convert it into a string
        file.write(str(soup.prettify()))
    print(urls)