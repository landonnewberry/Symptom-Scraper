from bs4 import BeautifulSoup
import requests
import threading
import json
import time

BASE_URL = 'https://questiondoctors.com/blog/page/'
OUTFILE = '../data/qd_corpus.txt'


def get_soup(url):
    try:
        resp = requests.get(url)
        text = resp.text
        soup = BeautifulSoup(text, 'html.parser')
    except:
        raise Exception('Could not get soup for {}'.format(url))
    return soup


class PostScraper(threading.Thread):

    global OUTFILE

    def __init__(self, url):
        super(PostScraper, self).__init__()
        self.url = url

    def main(self):
        time.sleep(2)           # don't want to hurt their site
        try:
            soup = get_soup(self.url)
            ps = soup.select('.post-entry p')
            title = soup.select_one('h1.entry-title.post-title').text
            text = ''
            for p in ps[:-1]:
                text += '{}'.format(p.text)
            item = {
                'title': title,
                'text': text[:-1].strip()
            }
            with open(OUTFILE, 'a') as outfile:
                if item['text'] != '':
                    outfile.write(json.dumps(item) + '\n')
        except:
            raise Exception('Issue scraping post: {}'.format(self.url))

    def run(self):
        self.main()

class QDScraper(threading.Thread):

    global BASE_URL

    @classmethod
    def page_valid(cls, soup):
        return soup.select_one('h1.title-404') == None

    @classmethod
    def main(cls):
        i = 1
        while(True):
            try:
                time.sleep(2)                       # don't want to hurt their site
                soup = get_soup(BASE_URL + str(i))
                if cls.page_valid(soup):
                    links = soup.select('header h1 a')
                    for a in links:
                        p = PostScraper(a.attrs['href'])
                        p.start()
                    i += 1
                else:
                    break
            except:
                raise Exception('Issue in main')
        print('{} - HALT'.format(i))

    def run(self):
        self.main()


if __name__=='__main__':
    t = QDScraper()
    t.start()