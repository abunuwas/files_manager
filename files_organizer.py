import concurrent.futures 
from concurrent.futures import ThreadPoolExecutor
import os
import time

import requests
from bs4 import BeautifulSoup

base_url = 'http://192.168.1.243:8000/'

base_target = '/Users/jose/Desktop'
dir_target = 'programming_books_sync'
target = os.path.join(base_target, dir_target)

def setup():
	if dir_target not in os.listdir(base_target):
		os.mkdir(os.path.join(base_target, dir_target))

def process_dir(current_dir, directory):
	print('Processing directory {}'.format(directory))
	nested = os.path.join(current_dir, directory[:-1])
	#os.mkdir(nested)
	print(nested)
	return nested
	#print(nested)
	#try:
	#	print('Directory {} not found. Creating directory...'.format(resource))
	#	#res = os.mkdir(nested)
	#	#print(res)
	#	print('Directory {} created.'.format(resource))
	#except FileExistsError: 
	#	print('Directory {} already exists. Nothing to do.'.format(resource))
	#return nested

def process_book(current_dir, resource, book_url):
	if resource not in os.listdir(current_dir):
		print('Book {} not in directory. Writing to file...'.format(resource))
		book = os.path.join(current_dir, resource)
		content = requests.get(book_url).content
		with open(book, 'wb') as file:
			file.write(content)
		print('Book {} copied.'.format(resource))
	else: print('Book {} already exists. Nothing to do.'.format(resource))

def get_links(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'html.parser')
	links = soup.find_all('li')
	return links

def process_link(link, url, current_dir, rest):
	resource = link.text
	print('Processing {}...'.format(resource))
	if resource.endswith('.pdf'):
		print('Resource is a book...')
		book_url = url+resource
		process_book(current_dir, resource, book_url)
	elif resource.endswith('/'):
		print('Resource is a directory...')
		new_dir = process_dir(current_dir, resource)
		dir_url = url+resource
		parse(dir_url, new_dir)
	else:
		print(url+resource) 
		rest.append(url+resource)

def process_link2(link, url, current_dir, rest):
	resource = link.text
	if resource.endswith('.pdf'):
		pass
	elif resource.endswith('/'):
		print(resource)
	else:
		print(resource[-1])

def parse(url, current_dir):
	errors = []
	print('Current url:', url)
	print('Current directory:', current_dir)
	rest = []
	links = get_links(url)
	print('Encountered {} resources'.format(len(links)))
	#for link in links[:20]:
	with ThreadPoolExecutor(max_workers=1000) as executor:
		futures = {executor.submit(process_link, link, url, current_dir, rest): link for link in links}
	for future in concurrent.futures.as_completed(futures):
		errors.append(future._exception)
	print(rest)
	time.sleep(3)
	for err in errors:
		if err is not None:
			print(err)
	return None


parse(base_url, target)





