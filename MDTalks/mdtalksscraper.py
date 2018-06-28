from bs4 import BeautifulSoup
import requests
import threading
import json
import time

BASE_URL = 'https://www.mdtalks.com/category/'
OUTFILE = '../data/mdtalks_corpus.txt'

class PostScraper(threading.Thread):
	'''
		Scrapes an individual post for topic and response.
		Stores the resulting JSON object.
	'''
	def __init__(self, url):
		super(PostScraper, self).__init__()
		self.url = url

	def run(self):
		try:
			time.sleep(1)				# don't want to hurt their site
			resp = requests.get(self.url)
			text = resp.text
			soup = BeautifulSoup(text, 'html.parser')
		except:
			raise ValueError('Unable to scrape URL: {}'.format(self.url))
		header = soup.select_one('.post-headline h1')
		header_text = header.text
		body = soup.select('.post-bodycopy.clearfix p')[:-1]
		body_text = str()
		footer = soup.select('.post-footer a')
		categories = []
		for a in footer:
			categories.append(a.text.upper())
		for p in body:
			body_text += p.text + ' '
		item = {
			'url': self.url,
			'header': header_text,
			'body': body_text,
			'categories': categories
		}
		with open(OUTFILE, 'a') as outfile:
			outfile.write(str(item) + '\n')


class ListScraper(threading.Thread):
	'''
		Scrapes a page listing forum posts.
		Determines whether or not to progress the next
		page.
	'''
	global BASE_URL

	def __init__(self, category, page=1):
		super(ListScraper, self).__init__()
		self.category = category
		self.page = page

	@classmethod
	def _page_valid(cls, soup):
		t = soup.select_one('#middle h2').text
		return (False if t == "Not Found" else True)

	def run(self):
		try:
			url = '{}{}/page/{}'.format(BASE_URL, self.category, self.page)
			time.sleep(5)				# don't want to hurt their site
			resp = requests.get(url)
			text = resp.text
			soup = BeautifulSoup(text, 'html.parser')
		except:
			raise ValueError('Unable to scrape URL: {}'.format(url))
		if self._page_valid(soup):
			headlines = soup.select('.post-headline h2 a')
			for h in headlines:
				ps = PostScraper(h.attrs['href'])
				ps.start()
			self.page += 1
			self.run()


class MDTalksScraper(threading.Thread):
	'''
		Responsible for scraping https://www.mdtalks.com for
		a corpus of illness reports in each category available.
		Deploys list scrapers for each category.
	'''

	categories = [
		'allergies', 'cardiology', 'dental', 'dermatology',
		'emergency-medicine', 'family-medicine', 'gastroenterology',
		'general-medicine', 'medical-legal', 'neurology',
		'nutrition', 'obstetrics-gynecology', 'oncology',
		'opthamology', 'orthopedics', 'other', 'otolaryngology-ent',
		'pediatrics', 'pharmacology', 'psychiatry', 'surgery'
	]

	global BASE_URL

	@classmethod
	def main(cls):
		for cat in cls.categories:
			time.sleep(60)				# don't want to hurt their site
			lt = ListScraper(cat)
			lt.start()


	def run(self):
		self.main()


if __name__=='__main__':
	t = MDTalksScraper()
	t.start()