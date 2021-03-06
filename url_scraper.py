import requests
import time
from bs4 import BeautifulSoup


def parse_source(html, encoding='utf-8'):
    parsed = BeautifulSoup(html, from_encoding=encoding)
    return parsed


def get_price(item, sizzle):
    resp = requests.get(item[1], timeout=3)
    resp.raise_for_status()
    parsed = parse_source(resp.content, resp.encoding)
    a = parsed.find('table', class_='a-lineitem')
    if a is not None:
        a = a.find('span', class_='a-size-medium a-color-price')
    else:
        a = parsed.find('span', class_='a-size-medium a-color-price')
    if a is None:
        a = parsed.find('b', class_='priceLarge')
    a = a.string.strip()
    if '-' in a:
        a = a.split(' - ')[0]
    price = a[1:].replace(',', '')
    sizzle.put((item[1], price))


def update_prices(tracking_list):
    from multiprocessing import Process, Queue
    price_queue = Queue()
    p = [Process(target=get_price, args=(i, price_queue,)) for i in tracking_list]
    for i in p:
        i.start()
    for i in p:
        i.join()
    result = []
    while not price_queue.empty():
        result.append(price_queue.get())
    return result

if __name__ == '__main__':
    urls = [{'url': 'http://www.amazon.com/gp/product/B0096VCUG6/ref=s9_simh_gw_p147_d0_i1?pf_rd_m=ATVPDKIKX0DER&pf_rd_s=center-3&pf_rd_r=1XR66059C6TSD0P2V1M6&pf_rd_t=101&pf_rd_p=1688200422&pf_rd_i=507846'},
            {'url': 'http://www.amazon.com/PS3-God-War-Collection-Playstation-3/dp/B008CP6MA2/ref=sr_1_1?s=videogames&ie=UTF8&qid=1403803209&sr=1-1&keywords=god+of+war'},
            {'url': 'http://www.amazon.com/Nike-371642-Legend-Dri-Fit-Tee/dp/B0036E2ZXM/ref=sr_1_1?s=sporting-goods&ie=UTF8&qid=1403803921&sr=1-1&keywords=nike'},
            {'url': 'http://www.amazon.com/Samsung-SM-G900H-Factory-Unlocked-International/dp/B00J4TK4B8/ref=sr_1_1?s=wireless&ie=UTF8&qid=1403804783&sr=1-1&keywords=samsung+galaxy+s5'}
    ]
    start = time.time()
    tic = lambda: 'at %1.1f seconds' % (time.time() - start)
    a = update_prices(urls)
    for i in a:
        print i[0], i[1]
    print tic()

