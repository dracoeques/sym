import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from sym.modules.utils.openaiapi import create_dalle_image, prompt_openai, get_openai_embedding
from sym.modules.db.models import *
from sym.modules.db.db import local_session

def get_or_create_media_source(name, url, session=None):
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    #prevent query params from polluting source url
    url = url.split("?")[0]
    
    ms = session.query(MediaSource)\
        .filter(MediaSource.url == url)\
        .first()
    if ms is not None:
        return ms
    ms = MediaSource()
    ms.name = name
    ms.url = url
    session.add(ms)
    session.commit()
    return ms


def get_existing_media_item(url, session=None):
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()
    
    mi = session.query(MediaItem)\
        .filter(MediaItem.source_url == url)\
        .first()
    return mi

def create_media_item(
        url=None,
        title=None,
        kind=None,
        summary=None,
        image=None,
        payload=None,
        id_source=None,
        session=None,
        body_text=None,
    ):

    if session is None:
        engine,session_factory = local_session()
        session = session_factory()

    mi = MediaItem()
    mi.source_url = url
    mi.kind = kind
    mi.title = title
    mi.summary = summary
    mi.image = image
    mi.payload = payload
    mi.id_source = id_source
    mi.body_text = body_text

    session.add(mi)
    session.commit()
    return mi

def get_main_body_text(url):

    #simple check to see if scraping is blocked 
    known_errors = [
        """JavaScript is not available"""
    ]

    try:
        # Fetch the webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Attempt to find the main content
        # Note: You might need to customize these selectors based on the specific website
        #main_content = soup.find('article') or soup.find('div', {'role': 'main'}) or soup.find('main')

        #if not main_content:
            # Fallback to using the whole body if specific main content is not found
        main_content = soup.body

        # Extract and return the text
        if not main_content:
            print(f"No body text detected")
            return None
        
        main_content =  main_content.get_text(separator='\n', strip=True)

        for estr in known_errors:
            if main_content.startswith(estr):
                return None

        return main_content

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None


def create_summary(body_text=None):
    if body_text is None:
        return ""
    prompt = f"""Create a short and concise summary for this content as 2 bullet points:\n {body_text}"""
    response_text,response = prompt_openai(prompt=prompt, model="gpt-3.5-turbo")
    return response_text

def generate_image(url, title, summary):
    prompt = f""" Create an image that accurately represents this content, 
                don't generate any font or text in the image just generate people, objects, shapes, places and things\n
            CONTENT:
            \n\n Title: {title}
            \n\n Summary: {summary}
        """
    return create_dalle_image(prompt=prompt)


def tag_media_item(title=None, body_text=None):
    if title is None and body_text is None:
        return []
    prompt = f"""Create list of categories / tags for this content in the form of a bulletted list, just return the tags without preamble:\n\n CONTENT:\n {title}\n {body_text}"""
    response_text,response = prompt_openai(prompt=prompt, model="gpt-3.5-turbo")

    tags = markdown_bullets_to_list(response_text)

    return tags

def save_media_tags(media_item, tags, session=None):
    if session is None:
        engine,session_factory = local_session()
        session = session_factory()

    assocs = []
    for raw_tag in tags:
        t = get_or_create_media_tag(raw_tag, session=session)
        t_assoc = associate_media_tag(media_item, t, session=session)
        assocs.append((t,t_assoc))
    return assocs

def get_or_create_media_tag(raw_tag, session=None):
    """ check if tag exists, if not create tag"""
    tag = raw_tag.lower().strip()
    t = session.query(MediaTag)\
        .filter(MediaTag.tag == tag)\
        .first()
    if t is None:
        t = MediaTag()
        t.tag = tag
        t.raw_tag = raw_tag
        e,r = get_openai_embedding(raw_tag)
        t.openai_tag_embedding = e
        session.add(t)
        session.commit()
    return t
    
def associate_media_tag(media_item, t, session=None):
    """ associate a media_item with a media_tag"""
    t_assoc = session.query(MediaItemTag)\
        .filter(MediaItemTag.id_media_item == media_item.id)\
        .filter(MediaItemTag.id_media_tag == t.id)\
        .first()
    if t_assoc is None:
        t_assoc = MediaItemTag()
        t_assoc.id_media_item = media_item.id
        t_assoc.id_media_tag = t.id
        session.add(t_assoc)
        session.commit()
    return t_assoc

def markdown_bullets_to_list(markdown_text):
    """
    Convert a markdown bulleted list into a list of strings.

    Parameters:
    markdown_text (str): The markdown bulleted list as a string.

    Returns:
    list: A list of strings, each representing a bullet point.
    """
    # Regular expression to find bulleted list items
    pattern = r'-\s*(.+)'
    # Find all matches and return them as a list
    return re.findall(pattern, markdown_text)

def get_or_generate_image(url, title, summary):
    img = find_main_image(url)
    
    if img is None:
        prompt = f""" Create an image that accurately represents this content, 
                don't generate any font or text in the image just generate people, objects, shapes, places and things\n
            CONTENT:
            \n\n Title: {title}
            \n\n Summary: {summary}
        """
        img = create_dalle_image(prompt=prompt)
    return img

def find_main_image(url):
    """
        prompt: create a python function using beautifulsoup4 and requests, which scrapes the webpage and then uses heuristic ranking to pick the most likely images from the list of images, if none of the images seem appropriate, the function should return no images
        
    """
    try:
        # Fetch the webpage
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all image tags
        images = soup.find_all('img')

        # Heuristic ranking variables
        min_size = (200, 200)  # Minimum width, height in pixels
        preferred_aspect_ratios = [(4, 3), (16, 9)]
        keyword_blacklist = ["logo", "icon", "ad", "banner", "sponsor"]

        best_score = 0
        best_image = None

        for img in images:
            src = img.get('src')
            try:
                width, height = int(img.get('width', 0)), int(img.get('height', 0))
            except:
                width, height = 0,0
            alt_text = img.get('alt', '').lower()
            score = 0

            # Check if image meets minimum size criteria
            if width >= min_size[0] and height >= min_size[1]:
                score += 1

            # Check for preferred aspect ratios
            for ratio in preferred_aspect_ratios:
                if height >0:
                    if abs(width/height - ratio[0]/ratio[1]) < 0.1:
                        score += 1
                        break

            # Check for blacklisted keywords in image src
            if src:
                if not any(keyword in src for keyword in keyword_blacklist):
                    score += 1

            # Check for meaningful alt text
            if alt_text:
                if len(alt_text) > 5 and not any(keyword in alt_text for keyword in keyword_blacklist):
                    score += 1

            # Update best image if current image has a higher score and meets min size requirements
            if score > best_score and width >= min_size[0] and height >= min_size[1]:
                best_score = score
                best_image = src

        #Handle relative image links
        if best_image is not None and best_image.startswith("http") != True:
            best_image = urljoin(url, best_image)
        return best_image

    except requests.RequestException as e:
        print(f"Error fetching the webpage: {e}")
        return None

