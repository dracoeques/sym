import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from sym.modules.discovery.crawlers.scrape_utils import \
    get_existing_media_item, get_or_generate_image, create_summary,\
    create_media_item, get_or_create_media_source, generate_image,\
    get_main_body_text, tag_media_item, save_media_tags
from sym.modules.db.db import local_session
import xml.etree.ElementTree as ET


def scrape_scidaily(session=None):
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    source_url = 'https://www.sciencedaily.com/'
    ms = get_or_create_media_source("Science Daily", source_url, session=session)

    rss_urls = [
        'https://www.sciencedaily.com/rss/all.xml',
        "https://www.sciencedaily.com/rss/top.xml",
        "https://www.sciencedaily.com/rss/top/science.xml",
        "https://www.sciencedaily.com/rss/top/health.xml",
        "https://www.sciencedaily.com/rss/top/technology.xml",
        "https://www.sciencedaily.com/rss/top/environment.xml",
        "https://www.sciencedaily.com/rss/top/society.xml",
        "https://www.sciencedaily.com/rss/strange_offbeat.xml",
        "https://www.sciencedaily.com/rss/most_popular.xml",
        "https://www.sciencedaily.com/rss/health_medicine/men's_health.xml",
        "https://www.sciencedaily.com/rss/mind_brain/stress.xml",
        "https://www.sciencedaily.com/rss/mind_brain/psychology.xml",
        "https://www.sciencedaily.com/rss/mind_brain/perception.xml",
        "https://www.sciencedaily.com/rss/mind_brain/memory.xml",
        "https://www.sciencedaily.com/rss/matter_energy/textiles_and_clothing.xml",
        "https://www.sciencedaily.com/rss/matter_energy/engineering_and_construction.xml",
        "https://www.sciencedaily.com/rss/matter_energy/energy_and_resources.xml",
        "https://www.sciencedaily.com/rss/matter_energy/telecommunications.xml",
        "https://www.sciencedaily.com/rss/matter_energy/automotive_and_transportation.xml",
        "https://www.sciencedaily.com/rss/matter_energy/aerospace.xml",
        "https://www.sciencedaily.com/rss/matter_energy/consumer_electronics.xml",
        "https://www.sciencedaily.com/rss/matter_energy/biochemistry.xml",
        "https://www.sciencedaily.com/rss/matter_energy/inorganic_chemistry.xml",
        "https://www.sciencedaily.com/rss/matter_energy/organic_chemistry.xml",
        "https://www.sciencedaily.com/rss/matter_energy/chemistry.xml",
        "https://www.sciencedaily.com/rss/matter_energy/thermodynamics.xml",
        "https://www.sciencedaily.com/rss/matter_energy/nanotechnology.xml",
        "https://www.sciencedaily.com/rss/computers_math/statistics.xml",
        "https://www.sciencedaily.com/rss/matter_energy/graphene.xml",
        "https://www.sciencedaily.com/rss/matter_energy/wearable_technology.xml",
        "https://www.sciencedaily.com/rss/matter_energy/technology.xml",
        "https://www.sciencedaily.com/rss/computers_math/computer_science.xml",
        "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
        "https://www.sciencedaily.com/rss/computers_math/quantum_computers.xml",
    ]

    data =[]
    for rss_url in rss_urls:
    
        items = scrape_rss_feed(rss_url)

        cur_items = 0
        max_items = 10

        for item in items:
            
            print(item)
            url,title = item["url"],item["title"]

            #check if this media item exists, if so skip
            existing_item = get_existing_media_item(url, session=session)
            if existing_item is not None:
                data.append(existing_item)
                continue
            
            #get a breadth of data each scrape
            cur_items +=1 
            if cur_items > max_items:
                continue
            
            body_text = get_main_body_text(url)
            summary = create_summary(body_text=body_text)
            #img = get_or_generate_image(url, title, summary)
            img = generate_image(url, title, summary)
            

            mi = create_media_item(
                url=url,
                title=title,
                kind="article",
                summary=summary,
                image=img,
                payload=None,
                id_source=ms.id,
                session=session,
                body_text=body_text,
            )
            data.append(mi)

            #add media tags
            tags = tag_media_item(title=title, body_text=body_text)
            assocs = save_media_tags(mi, tags, session=session)
            
    return data
    


def scrape_rss_feed(url):
    # Fetch the RSS feed content
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return "Failed to retrieve the RSS feed: Status code {}".format(response.status_code)

    # Parse the XML content
    root = ET.fromstring(response.content)

    articles = []
    for item in root.findall('.//item'):
        title = item.find('title').text if item.find('title') is not None else None
        link = item.find('link').text if item.find('link') is not None else None

        articles.append({'title': title, 'url': link})

    return articles


def scrape_articles(url):
    

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print( "Failed to retrieve the webpage: Status code {}".format(response.status_code))        
        return []

    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find all article elements - you might need to adjust the selector based on the website's structure
    articles = soup.find_all('div', class_='latest-research')  # Example, adjust the class name based on actual website

    # Extract the URLs and titles
    article_list = []
    for article in articles:
        title = article.find('a').text.strip()  # Adjust based on the actual structure of the webpage
        url = article.find('a')['href']  # Adjust based on the actual structure of the webpage

        # Add the article to the list
        article_list.append({"url": url, "title": title})

    return article_list

if __name__ == "__main__":
    # Run the scraper and print results
    engine,session_factory = local_session()
    session = session_factory()
    data = scrape_scidaily(session=session)
    print(json.dumps([x.to_dict() for x in data], indent=2))
    # for item in data:
    #     print(item)