"""
This file contains functions that crawl wikipedia. To download images use:

python wiki_crawler.py <url> <max_pages>

Alex Angus

May 9th, 2020
"""

import requests
from bs4 import BeautifulSoup
import sys
import shutil

class WikiScraper():
    def __init__(self, image_folder="./wiki_scrape_images/", max_pages=10):
        self.image_folder = image_folder
        self.max_pages = max_pages
        
    def scrape_page(self, url, page_num):
        """
        returns the title and a list of wikipedia links on the page
        """
        r = requests.get(url)                               # request page
        soup = BeautifulSoup(r.text, 'html.parser')         # convert html to text
        page_links = []
        for link in soup.findAll('a'):
            link_text = link.get('href')
            if link_text != None:
                if ('#' not in link_text):
                    if 'http' not in link_text:
                        link_text = 'https://en.wikipedia.org' + link_text
                        pass
                    if 'en.' in link_text:
                        page_links.append(link_text)
        header = soup.find(id='firstHeading')
        img_tags = soup.find_all('img')
        image_links = set(tag['src'] for tag in img_tags)
        clean_links = []
        for link in image_links:
            if ('.jpg' in link) or ('.png' in link):
                clean_links.append(link)
        if header is not None:
            title = header.text
        else:
            title = url
        return title, page_links, clean_links
        
    def download_image(self, url):
        """
        downloads the image at the url specified to a file specified by filename
        """

        if (url is None) or ('/static/' in url) or ('Flag_of' in url):
            return
        count = 1
        image_name = ""
        while True:
            char = url[-count]
            if char != '/':
                image_name = char + image_name
                count += 1
            else:
                break
        try:
            r = requests.get(url, stream=True)
        except:
            print("This link didn't work: ")
            print(url)
            return
        if r.status_code == 200:             
            with open(self.image_folder + image_name, 'wb') as f:             #create image file
                shutil.copyfileobj(r.raw, f)
        else:
            print("Request was unsuccessful! :(")
            sys.exit()
            
    def fix_url(self, url):
        """
        Makes the url findable.
        """
        if 'https://' not in url:
            for index, char in enumerate(url):
                if char == '/':
                    if url[index+1] == '/':
                        url = url[index+1:]
                    else:
                        url = url[index:]
                    url = 'https:/' + url
                    return url
        else: 
            return url
        return 'https:/' + url
                
        
    def crawl(self, starting_url):
        """
        This function crawls wikipedia collecting links and visiting other wikipedia 
        pages.
        """
        links = [starting_url]
        image_links = []
        report = open("Wikipedia_Crawl.txt", 'w')
        page_num = 1
        while (len(links) > 0) and (page_num <= self.max_pages):
            title, new_links, new_image_links = self.scrape_page(links.pop(0), page_num)
            links.extend(new_links)
            image_links.extend(new_image_links)
            page_num += 1
            report.write(title + '\n')
        report.close()
        
        for image_link in image_links:
            self.download_image(self.fix_url(image_link))

def main():
    ws = WikiScraper(max_pages=int(sys.argv[2])).crawl(sys.argv[1])
        
if __name__ == "__main__":
    main()
        
