import requests_cache
requests_cache.install_cache('my_cache')
import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup

main_page_url = "https://sarabrewer.com/"

def fetch_url_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return None

def extract_blog_post_urls(main_page_content):
    soup = BeautifulSoup(main_page_content, 'html.parser')
    blog_posts = soup.select('h2.blog__title a')
    return [urljoin(main_page_url, post['href']) for post in blog_posts]

def extract_post_data(post_page_content):
    soup = BeautifulSoup(post_page_content, 'html.parser')
    title = soup.find('h1', class_='blog__title').text.strip()
    # key_points = soup.find_next_sibling('h2[text="What You\'ll Learn from this Episode:"]').find_all('li').text.strip()
    episode_transcript_item = soup.find(lambda tag: tag.name == 'h2' and "Full Episode Transcript:" in tag.text)
    transcript_div = episode_transcript_item.find_next('div')
    transcript = [paragraph.text.strip() for paragraph in transcript_div.find_all('p')]
    return title, transcript

def main():
    main_page_content = fetch_url_content(urljoin(main_page_url, 'blog'))
    
    if main_page_content:
        blog_post_urls = extract_blog_post_urls(main_page_content)
        print(blog_post_urls)
        for url in blog_post_urls:
            post_page_content = fetch_url_content(url)
            if post_page_content:
                title, transcript = extract_post_data(post_page_content)
                print(f"Title: {title}\nTranscript: {transcript}")
    else:
        print("Failed to fetch main page content")

if __name__ == "__main__":
    main()