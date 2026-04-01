import time

import requests
from bs4 import BeautifulSoup
import re
import os
import pandas as pd

crawled_pages = 0

class DocCrawler:

    def __init__(self):
        self.count_pages = 0

    def discover_urls(self, page_url: str, sub_url: str, soup: BeautifulSoup) -> list[str]:
        """Collect absolute same-origin URLs from anchors (fragments stripped)."""
        links = soup.find_all('a', attrs={'href': re.compile("")})
        urls = []
        for link in links:
            # display the actual urls
            lnk_str = link.get('href')
            if lnk_str not in urls and lnk_str != (page_url+"/") and lnk_str.startswith((sub_url)):
                urls.append(link.get('href'))
        return urls

    def download_page(self, url: str, timeout: int):
        
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
        
    def create_dataset(self, base_url: str, sub_url: str, crawled:list[str], timeout: int = 15, delay: int = 2, max_pages:int = 2):
        if sub_url in crawled or self.count_pages==max_pages:
            return True
        print(f"Crawling: {sub_url}")
        #dataset = []
        #sub_url = ""
        #if base_url != this_url:
        #    sub_url = this_url.replace(base_url, "")
        soup = self.download_page((base_url+sub_url), timeout)
        urls = self.discover_urls(base_url,sub_url, soup)
        
        with open(f"output/{sub_url}.html", "w", encoding = 'utf-8') as file:
            # prettify the soup object and convert it into a string
            file.write(str(soup.prettify()))
        
        a = pd.DataFrame([[sub_url, base_url]],
                            columns=['url','base_url'])
        a.to_csv('output/metadata.csv', mode='a', index=False, header=False)
        crawled.append(sub_url)
        self.count_pages += 1
        for url in urls:
            time.sleep(delay)
            self.create_dataset(base_url,url,timeout)
        return False

if __name__ == "__main__":
    url =  "https://www.th-owl.de/skim/dokumentation/"
    with open("output/dokumentation.html") as html:
        soup = BeautifulSoup(html, "html.parser")#download_page(url = url, timeout=15)
    print(soup)
    crawler = DocCrawler()
    sub_url = "/skim/dokumentation"
    urls = crawler.discover_urls(sub_url, sub_url, soup)
    url = "dokumentation"
    
    #if not os.path.exists(f"output/{url}.html"):
    #    os.makedirs(f"output/{url}.html")
    
    print(urls)