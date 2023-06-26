#!/usr/bin/python3

# simplecurl.py
# Ron Newsome, Jr.
# 2018-04-22
# Updated: 2022-03-10

import os, requests, shutil

def get_contents(url):
	h = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36'}
	r = requests.get(url, headers=h)
	return r.text

def post_contents(url, params):
	h = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
		"Content-type": "application/x-www-form-urlencoded"}
	r = requests.post(url, headers=h, data=params)
	return r.text

def save_image(remoteurl, localpath, preview=False):
	print('Downloading image...')
	r = requests.get(remoteurl, stream=True)
	if r.status_code == 200:
		r.raw.decode_content = True
		with open(localpath,'wb') as f:
			shutil.copyfileobj(r.raw, f)
		print('Downloaded: ' + remoteurl)
		print('Saved as:   ' + localpath.split('/')[-1])
		if preview:
			os.system(f'feh {localpath}')
	else:
		print("Couldn't retreive image.")

def get(url):
	return get_contents(url)

def put(url, params):
	post_contents(url, params)
