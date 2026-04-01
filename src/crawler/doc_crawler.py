import time

import requests
from bs4 import BeautifulSoup
import os
import pandas as pd

crawled_pages = 0

class DocCrawler:

    def __init__(self):
        self.count_pages = 0

    def discover_urls(self, page_url: str, sub_url: str, soup: BeautifulSoup) -> list[str]:
        """Collect absolute same-origin URLs from anchors (fragments stripped)."""
        links = soup.find_all('a')
        urls = []
        for link in links:
            # display the actual urls
            lnk_str = link.get('href')
            if lnk_str is not None:
                if lnk_str not in urls and lnk_str != (page_url) and lnk_str.startswith((sub_url)):
                    urls.append(link.get('href'))
        return urls

    def download_page(self, url: str, timeout: int):
        # Get page
        try:
            page = requests.get(url=url, timeout=timeout)
            page.raise_for_status()
            html = page.text
        except Exception as e:
            print(e)
            return None
        
        soup = BeautifulSoup(html, "html.parser")
        # Clean up html
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()
        
        return soup
        
    def create_dataset(self, base_url: str, sub_url: str, root_url:str, crawled:list[str], timeout: int = 15, delay: int = 2, max_pages:int = 2):
        if sub_url in crawled:
            if sub_url == root_url and self.count_pages == 0:
                pass
            else:
                print(f"URL {sub_url} already crawled.")
                return True
        print("Delay before next crawl")
        time.sleep(delay)
        print(f"Crawling: {sub_url} --------- ({self.countpages}/{max_pages})")
        #dataset = []
        #sub_url = ""
        #if base_url != this_url:
        #    sub_url = this_url.replace(base_url, "")
        soup = self.download_page(base_url+sub_url, timeout)
        if soup is not None:
            urls = self.discover_urls(base_url,sub_url, soup)
            print(f"Found {len(urls)} sub-urls")
            if not os.path.exists(f"output{sub_url}"):
                print(f"Creating new subdirectory {sub_url}")
                os.makedirs(f"output{sub_url}")
            with open(f"output{sub_url}output.html", "w", encoding = 'utf-8') as file:
                # prettify the soup object and convert it into a string
                file.write(str(soup.prettify()))
                print(f"Saved file to output{sub_url}output.html")
            a = pd.DataFrame([[sub_url, base_url]], columns=['url','base_url'])
            a.to_csv('output/metadata.csv', sep = ";", mode='a', index=False, header=False)
            crawled.append(sub_url)
            self.count_pages += 1
            for url in urls:
                if self.count_pages == max_pages:
                    print("The max number of pages was reached")
                    break
                elif url not in crawled:
                    self.create_dataset(base_url,url, root_url, crawled, timeout, delay, max_pages)
        else:
            print("This page seems to be empty")
        return False

if __name__ == "__main__":
    #url =  "https://www.th-owl.de/skim/dokumentation/"
    #with open("output/dokumentation.html") as html:
    #    soup = BeautifulSoup(html, "html.parser")#download_page(url = url, timeout=15)
    #print(soup)

    
    #urls = crawler.discover_urls(sub_url, sub_url, soup)
    #url = "dokumentation"
    
    #print(urls)
    crawler = DocCrawler()
    base_url = "https://www.th-owl.de"
    sub_url = "/skim/dokumentation/"
    already_crawled = pd.read_csv("output/metadata.csv", sep = ';')['url'].values.tolist()
    timeout = 15
    delay = 5
    max_pages = 150

    crawler.create_dataset(base_url, sub_url, sub_url, already_crawled,timeout,delay,max_pages) #already_crawled