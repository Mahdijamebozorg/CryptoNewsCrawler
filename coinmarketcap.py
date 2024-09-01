import requests
from bs4 import BeautifulSoup
import time
import warnings
import dateparser
import utills as utills
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import csv
from datetime import datetime

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# -------------------------------------------
def get_coinmarketcap_article_selenium(url):
    options = Options()
    options.headless = True  # Run headlessly
    service = Service('chromedriver.exe')  # Update with your path to chromedriver

    driver = webdriver.Chrome(service=service, options=options)
    driver.get(url)

    try:
        # Scroll down to load all dynamic content
        driver.execute_script("window.scrollTo(0, 800)")
        time.sleep(2)

        # Extract content using Selenium
        soup = BeautifulSoup(driver.page_source, 'lxml')
        driver.quit()

        title_tag = soup.find('h1')
        date_span = soup.find('span', class_='sc-6249f85d-5 dwOmQo')

        # Check if title and date exist
        if title_tag:
            title = title_tag.text.strip()
        else:
            print(f"Missing title in article at {url}")
            return None
        
        if date_span:
            date_text = date_span.text.strip()
            date = dateparser.parse(date_text)  # Use dateparser to parse relative time
        else:
            print(f"Missing date in article at {url}")
            return None
        
        # Extract article content correctly
        article_tag = soup.find('article', class_='sc-65e7f566-0 sc-6249f85d-0 ktlJNL ewhPlu')
        if article_tag:
            content_elements = article_tag.find_all(['div','p','h2','h3','a'])
            if content_elements:
                content = ' '.join([elem.get_text(strip=True) for elem in content_elements])
            else:
                print(f"Missing article content in article at {url}")
                return None
        else:
            print(f"Missing article content in article at {url}")
            return None

        print(f'parsed: title: {title}: url: {url}, date: {date}, content: {content}')
        return {'title': title,'url': url,'date': date,'content': content}
    
    except Exception as e:
        print(e)
        driver.quit()
        return None


# -------------------------------------------
def save_article_to_csv(article, filename='coinmarketcap_articles.csv'):
    # Define the CSV file headers
    fieldnames = ['title', 'url', 'date', 'content']

    # Open the CSV file for writing
    with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Convert the date to string format if it's a datetime object
        if isinstance(article['date'], datetime):
                article['date'] = article['date'].strftime('%Y-%m-%d %H:%M:%S')

        writer.writerow(article)


# -------------------------------------------
def crawl_coinmarketcap():
    base_url = "https://coinmarketcap.com"
    sub_url = base_url + "/sitemap/community-articles/"
    
    page_number = 1

    while True:
        try:
            print(f"Fetching page {page_number}")
            response = requests.get(f"{sub_url}?page={page_number}", headers=utills.get_random_headers(), verify=False)
            response.raise_for_status()  # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, 'lxml')

            # Find all article links
            links_found = 0
            for link in soup.find_all('a', href=True):
                href = link['href']
                if '/community/articles/' in href:
                    links_found += 1
                    # Construct the full URL if it's a relative URL
                    article_url = href if href.startswith('http') else base_url + href
                    article_info = get_coinmarketcap_article_selenium(article_url)
                    if article_info:
                        save_article_to_csv(article_info)        


            if links_found == 0:
                # No more articles found, break out of the loop
                break

            page_number += 1
            time.sleep(10)  # Pause between requests to avoid rate-limiting

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            time.sleep(10)  # Exponential backoff
            continue



if __name__ == "__main__":
    coinmarketcap_articles = crawl_coinmarketcap()
