import requests_cache
requests_cache.install_cache('my_cache')
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
import json
import re

all_paragraphs = []
main_page_url = "https://sarabrewer.com/"

def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def get_post_list_page_urls(main_blog_page_content):
    soup = BeautifulSoup(main_blog_page_content, 'html.parser')
    list_pages = soup.select('a.pag__link')
    return [urljoin(main_page_url, urljoin('blog', page['href'])) for page in list_pages]

def extract_blog_post_urls(post_list_page_content):
    soup = BeautifulSoup(post_list_page_content, 'html.parser')
    blog_posts = soup.select('h2.blog__title a')
    return [urljoin(main_page_url, post['href']) for post in blog_posts]

def extract_post_data(post_page_content):
    soup = BeautifulSoup(post_page_content, 'html.parser')
    title = soup.find('h1', class_='blog__title').text.strip()
    # key_points = soup.find_next_sibling('h2[text="What You\'ll Learn from this Episode:"]').find_all('li').text.strip()
    episode_transcript_item = soup.find(lambda tag: "Full Episode Transcript:" in tag.text)
    try:
        transcript_div = episode_transcript_item.find_next('div')
        transcript_array = [paragraph.text.strip() for paragraph in transcript_div.find_all('p')]
        raw_transcript = '\n\n'.join(transcript_array)
    except AttributeError:
        print(title)
        transcript_array = []
        raw_transcript = ''
    return title, raw_transcript, transcript_array

def get_repeats(items):
    repeats = []
    for item in items:
        if item[1] > 1 and ": " not in item[0]:
            repeats.append(item)
    return repeats

def extract_episode_number(title):
    match = re.search(r'\d+', title)
    return int(match.group()) if match else float('inf')

def main():
    main_page_content = fetch_url_content(urljoin(main_page_url, 'blog'))
    
    if main_page_content:
        post_list_pages = list(set(get_post_list_page_urls(main_page_content)))
        all_blog_posts = []

        for post_list_page_url in post_list_pages:
            post_list_page_content = fetch_url_content(post_list_page_url)
            blog_post_urls = extract_blog_post_urls(post_list_page_content)
            for url in blog_post_urls:
                post_page_content = fetch_url_content(url)
                if post_page_content:
                    title, raw_transcript, transcript_array = extract_post_data(post_page_content)
                    all_paragraphs.extend(transcript_array)
                    all_blog_posts.append({
                        "title": title,
                        "transcript_array": transcript_array,
                        "raw_transcript": raw_transcript
                    })
    else:
        print("Failed to fetch main page content")

    sorted_blog_posts = sorted(all_blog_posts, key=lambda post: extract_episode_number(post['title']))
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_blog_posts, f, ensure_ascii=False, indent=4, sort_keys=True)

    paragraph_counter = Counter(all_paragraphs)
    top_sayings = get_repeats(paragraph_counter.most_common(30))

if __name__ == "__main__":
    main()