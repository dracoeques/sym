import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from sym.modules.discovery.crawlers.scrape_utils import \
    get_existing_media_item, get_or_generate_image, create_summary,\
    create_media_item, get_or_create_media_source, generate_image,\
    get_main_body_text, tag_media_item, save_media_tags
from sym.modules.db.db import local_session


# URL of Hacker News front page

def scrape_hacker_news(session=None):

    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    source_urls = [
        "https://news.ycombinator.com/",
        "https://news.ycombinator.com/?p=2",
        "https://news.ycombinator.com/?p=3",
        "https://news.ycombinator.com/?p=4"
    ]

    ms = get_or_create_media_source("Hacker News", "https://news.ycombinator.com/", session=session)
    for source_url in source_urls:
        links = hn_get_top(url=source_url)
        data = []
        for item in links:
            print(item)
            url,title = item["url"],item["title"]

            #check if this media item exists, if so skip
            existing_item = get_existing_media_item(url, session=session)
            if existing_item is not None:
                data.append(existing_item)
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
            

            #print(json.dumps(mi.to_dict(), indent=2))

    return data


def hn_get_top(url = "https://news.ycombinator.com/"):
    """ Get all links with a title and url """
    # Fetch the content from the URL
    response = requests.get(url)
    content = response.content

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Find the story elements
    stories = soup.find_all('tr', class_='athing')

    # Extract and store data
    extracted_data = []
    for story in stories:
        links = story.find_all('a')
        for link in links:
            if link is None:
                continue
            title = link.get_text()
            link = link['href']
            if title and link.startswith("http"):
                extracted_data.append({'title': title, 'url': link})
    
    return extracted_data



if __name__ == "__main__":
    # Run the scraper and print results
    
    engine,session_factory = local_session()
    session = session_factory()
    data = scrape_hacker_news(session=session)
    print(json.dumps([x.to_dict() for x in data], indent=2))
    # for item in data:
    #     print(item)