import requests
import time
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import re
import html5lib


def downloader(url):
    r = requests.get(url)
    return r.text if r.status_code == 200 else None


# Remove references like [123]
def without_references(text):
    return re.sub(r'\[\d+\]', '', text)


def get_content(content):
    soup = BeautifulSoup(content, 'html5lib')

    table = soup.find("table", {'class': "sortable wikitable"})
    valid_links = []
    for link in table.find_all('a'):
        url = link.get('href', '')
        if url not in valid_links and url.endswith('Grand_Prix'):
            valid_links.append(link)

    paragraphs = (soup.find("span", {'id': "Opening_rounds"})
                  .find_parent()
                  .fetchNextSiblings("p"))

    scraped_info = []
    for i in range(len(valid_links)):
        info = {'title': valid_links[i].text.strip(),
                'content': without_references(paragraphs[i].text.strip())}
        scraped_info.append(info)
    return scraped_info


def generate_markdown_page(scraped_info):
    markdown_content = ("# Races of 2023 Formula One World Championship\n\n"
                        "Formula One 2023 Season was to be honest pretty lame "
                        "but hey! True fans will always watch and cheer so in order to "
                        "remember all those races here we have a collection reminiscing every "
                        "race of 2023 one by one :).\n\n"
                        "## The List of Races\n\n")

    for item in scraped_info:
        file_name = item['title'].replace(" ", "")
        markdown_content += (f"### {item['title']}\n\n"
                             f"{item['content']}\n\n"
                             f"[Read More](./{file_name}.md)\n\n")

    with open('./index.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)


def generate_subpages(scraped_info):
    for item in scraped_info:
        soup = search_additional_info(f"{item['title']} 2023 wiki")

        additional_info = soup.find_all("p")
        infobox_image_place = soup.find("td", {'class': "infobox-image"})
        image_source = "https:" + infobox_image_place.find("img")['src']

        markdown_page = (f"# {item['title']}\n\n"
                         f"[return to main page](./index.md)\n\n"
                         f"## Race Layout: \n\n "
                         f"![The circuit layout]({image_source})\n\n"
                         f"## Description\n\n")
        for paragraph in additional_info:
            markdown_page += f"{without_references(paragraph.text.strip())} \n\n"

        file_name = item['title'].replace(" ", "")
        with open(f"./{file_name}.md", 'w', encoding='utf-8') as file:
            file.write(markdown_page)


def search_additional_info(query):
    response = DDGS().text(query, max_results=1)
    for result in response:
        page = downloader(result['href'])
        return BeautifulSoup(page, 'html5lib')


def main():
    page_text = downloader('https://en.wikipedia.org/wiki/2023_Formula_One_World_Championship')
    if page_text:
        content = get_content(page_text)
        generate_subpages(content)
        generate_markdown_page(content)
    else:
        print("Problem z popraniem strony :(")


main()
