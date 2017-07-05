from collections import OrderedDict
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def scrape_page(url):
    """
    """
    r = requests.get(url)
    content = r.content.decode('utf-8')

    page = BeautifulSoup(content, 'html.parser')

    title = page.find('h1', {'id': 'title'})
    book_name = ' - '.join(x.text.strip() for x in title.findAll('span'))

    result = dict(book_name=book_name,
                  categories=OrderedDict())

    categories = page.find_all('li', {'class': 'zg_hrsr_item'})
    for c in categories:
        name = '/'.join(x.text for x in c.find_all('a'))
        rank = int(c.find('span', {'class': 'zg_hrsr_rank'}).text[1:])
        result['categories'][name] = rank

    return result


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