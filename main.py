import json
import re
from collections import Counter
from urllib.parse import urljoin

import requests
import requests_cache
from bs4 import BeautifulSoup
import nltk

requests_cache.install_cache('my_cache')
nltk.download('punkt')

all_paragraphs = []
main_page_url = "https://sarabrewer.com/"


def fetch_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(e)
        return None
    return response.text


def get_post_list_page_urls(main_blog_page_content):
    soup = BeautifulSoup(main_blog_page_content, 'html.parser')
    list_pages = soup.select('a.pag__link')
    page_urls = [urljoin(main_page_url, urljoin('blog', page['href'])) for page in list_pages]
    page_urls.append(urljoin(main_page_url, urljoin('blog',"?page=13")))
    return page_urls


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
        raw_transcript = '\n'.join(transcript_array)
        episode_tokens = nltk.word_tokenize(raw_transcript)
        token_count = len(episode_tokens)
    except AttributeError:
        print(f"{title} | Something went wrong when extracting data from the post.")
        transcript_array = []
        raw_transcript = ''
    return title, raw_transcript, transcript_array, token_count


def extract_episode_number(title):
    match = re.search(r'\d+', title)
    return int(match.group()) if match else float('inf')


def get_repeats(items):
    repeats = [(item, count) for item, count in items if count > 1 and ": " not in item]
    return repeats


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
                    title, raw_transcript, transcript_array, token_count = extract_post_data(post_page_content)
                    if "replay" not in title.lower() and not any(post["title"] == title for post in all_blog_posts): # Check for duplicates and don't double count replays
                        all_paragraphs.extend(transcript_array)
                        all_blog_posts.append({
                            "title": title,
                            "transcript_array": transcript_array,
                            "raw_transcript": raw_transcript,
                            "token_count": token_count
                        })
    else:
        print("Failed to fetch main page content")

    sorted_blog_posts = sorted(all_blog_posts, key=lambda post: extract_episode_number(post['title']))
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(sorted_blog_posts, f, ensure_ascii=False, indent=4, sort_keys=True)

    paragraph_counter = Counter(all_paragraphs)
    top_sayings = get_repeats(paragraph_counter.most_common(150))

if __name__ == "__main__":
    main()