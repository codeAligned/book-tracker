import json
import random
from collections import OrderedDict
from pprint import pprint
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup

from config import proxies, user_agents


def get_proxy():
    r = requests.get('http://pubproxy.com/api/proxy')
    if not r.ok:
        return random.choice(proxies)

    content = json.loads(r.content)
    return content['data'][0]['ipPort']


def get_user_agent():
    return random.choice(user_agents)


def get_page_content_with_requests(url):
    headers = {
        'Connection': 'close',
        'User-Agent': get_user_agent()
    }

    proxy = get_proxy()
    print('Proxy:', proxy)
    r = requests.get(url, proxies=dict(http=proxy), headers=headers)
    content = r.content.decode('utf-8')
    return content


def scrape_page_with_requests(url):
    """
    """
    result = ''
    content = get_page_content_with_requests(url)
    page = BeautifulSoup(content, 'html.parser')

    title = page.find('h1', {'id': 'title'})
    if title is None:
        if 'Robot Check' in content:
            print('Oh-oh, robot check failed. Shuffle proxy list and/or UA list...')
        else:
            print('The title is missing for "{}". Skipping :-('.format(url))
        open('content.txt', 'w').write(content)
        return
    book_name = ' - '.join(x.text.strip() for x in title.findAll('span'))

    result = dict(book_name=book_name,
                  categories=OrderedDict())

    categories = page.find_all('li', {'class': 'zg_hrsr_item'})
    for c in categories:
        name = '/'.join(x.text for x in c.find_all('a'))
        rank = int(c.find('span', {'class': 'zg_hrsr_rank'}).text[1:])
        result['categories'][name] = rank

    # Add the Amazon best seller rank as another category
    text = page.find('li', {'id': 'SalesRank'}).text
    tokens = [a for a in text.split('\n') if a]
    name = tokens[0].split(':')[0]
    rank = int(tokens[1].split()[0][1:].replace(',', ''))
    result['categories'][name] = rank

    return result


def scrape_page_with_puppeteer(url):
    session = HTMLSession()
    r = session.get(url)
    r.html.render(retries=1, wait=3.0)
    page = r.html
    title = page.find('#title')[0].find('span')
    if title is None:
        if 'Robot Check' in r.content:
            print('Oh-oh, robot check failed. Shuffle proxy list and/or UA list...')
        else:
            print('The title is missing for "{}". Skipping :-('.format(url))
        open('content.txt', 'w').write(r.content)
        return
    book_name = ' - '.join(x.text.strip() for x in title)

    result = dict(book_name=book_name,
                  categories=OrderedDict())

    categories = page.find('#SalesRank > ul > li')

    for c in categories:
        name = '/'.join(x.text.replace(' >', '') for x in c.find('a'))
        rank = int(c.find('span')[0].text[1:])
        result['categories'][name] = rank

    # Add the Amazon best seller rank as another category
    text = page.find('#SalesRank')[0].text
    tokens = [a for a in text.split('\n') if a][0].split(':')
    name = tokens[0]
    rank = int(tokens[1].strip().split(' ')[0][1:].replace(',', ''))
    result['categories'][name] = rank

    return result


scrape_page = scrape_page_with_puppeteer


def main():
    book_urls = (
        'https://www.amazon.com/Mastering-Kubernetes-Gigi-Sayfan-ebook/dp/B01MXVUXDY',
        'https://www.amazon.com/Mastering-Kubernetes-Gigi-Sayfan/dp/1786461005'
    )

    for url in book_urls:
        r = scrape_page(url)
        pprint(r)
        print('-' * 10)


if __name__ == '__main__':
    main()
