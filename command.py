#!/usr/bin/python
# kodi/command.py
# Ron Newsome, Jr.
# 2018-05-12

import simplecurl, json, re
import os.path

class Player:
	def __init__(self):
		self.url = self.__detect_Kodi()
		self.specials = self.__get_specials()

	def __detect_Kodi(self):
		url = 'http://192.168.10.102:8080/jsonrpc?request='
		# Simply test if Kodi is running.
		self.introspect(url)
		# Eventually code a way to automatically detect Kodi
		# on the local network, but for now,
		# change this to the URL where Kodi is located.
		return url

	def __pretty_print(self, str):
		doc = json.loads(str)
		return json.dumps(doc, indent=4)

	def __get_specials(self):
		# Some edge cases involving non-alphanumeric characters
		mypath = os.path.abspath(os.path.dirname(__file__))
		jsonfile = os.path.join(mypath, 'specials.json')
		f = open(jsonfile)
		lst = f.read()
		f.close()
		return json.loads(lst)

	def introspect(self, url):
		obj = {
			"jsonrpc":"2.0","method": "JSONRPC.Introspect",
			"params":{
				"filter": {
					"id":"AudioLibrary.GetAlbums",
					"type": "method"
				}
			},
			"id":1
		}
		cmd = json.dumps(obj)
		return simplecurl.get_contents(url + cmd)

	def play_pause(self):
		params = {
			"jsonrpc":"2.0","method": "Player.PlayPause",
			"params":{"playerid":1},
			"id":1
		}
		cmd = json.dumps(params)
		res = simplecurl.get_contents(self.url + cmd)
		msg = json.loads(res)
		if 'error' in msg:
			return "Unable to start playback"
		return self.get_whats_playing()

	def stop(self):
		params = {
			"jsonrpc":"2.0","method": "Player.Stop",
			"params":{"playerid":1},
			"id":1
		}
		cmd = json.dumps(params)
		simplecurl.get_contents(self.url + cmd)
		return 'Stopping Kodi.'

	def __begin(self, item):
		# Begin playback of an item using it's path
		# resume from where i left off, if applicable.
		params = {
			"jsonrpc":"2.0","method": "Player.Open",
			"params":{
				"item": {"file": item['file']},
				"options": {"resume": True}
			}, "id":1
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		if item['label']:
			return "Playing '{}'".format(item['label'])
		elif item['title']:
			return "Playing '{}'".format(item['title'])
		else:
			return self.__pretty_print(results)

	def scan(self):
		# Scan the video library only.
		params = {
			"jsonrpc":"2.0","method": "VideoLibrary.Scan", "id": 1,
			"params": {"showdialogs": True}
		}
		cmd = json.dumps(params)
		simplecurl.get_contents(self.url + cmd)
		return 'Scanning the video library'

	def display_info(self):
		# Activates On Screen Display
		obj = {"jsonrpc":"2.0","method": "Input.ShowOSD", "id":1}
		cmd = json.dumps(obj)
		self.__pretty_print( simplecurl.get_contents(self.url + cmd) )
		return self.get_whats_playing()

	def to_home_screen(self):
		# Goes to the home screen
		obj = {"jsonrpc":"2.0","method": "Input.Home", "id":1}
		cmd = json.dumps(obj)
		self.__pretty_print( simplecurl.get_contents(self.url + cmd) )
		return self.get_whats_playing()

	def is_playing(self):
		obj = {
			"jsonrpc": "2.0", "method": "Player.GetProperties",
			"params":{
				"properties": ["speed"],
				"playerid": 1
			},
			"id": 1
		}
		cmd = json.dumps(obj)
		res = simplecurl.get_contents(self.url + cmd)
		playing = json.loads(res)
		if playing['result']['speed'] == 0:
			return False
		else:
			return True
	
	def get_whats_playing(self):
		api_params = {
			"jsonrpc": "2.0","method": "Player.GetItem",
			"params": {
				"properties": ["showtitle", "title", "season", "episode"], "playerid": 1
			},
			"id": "VideoGetItem"
		}

		jsonp = json.dumps(api_params)
		jstr = simplecurl.get_contents(self.url + jsonp)
		doc = json.loads(jstr)
		resitem = doc['result']['item']
		try:
			state = '[playing]' if self.is_playing() else '[paused]'
			info = '{} - {}x{} - {} {}'.format(resitem['showtitle'], str(resitem['season']), 
				str(resitem['episode']), resitem['title'], state)
		except:
			info = 'Nothing playing.'
		return info

	def list_episodes(self, q, andprint=True):
		# Searches for a show, and prints all episodes
		special = self.__is_special(q)
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
			"params": {
				"filter": {"field": "title", "operator":"contains", "value": q},
				"properties": ["title", "file"],
				"sort": {"order": "ascending", "method": "title", "ignorearticle": True}
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads(results)
		try:
			self.__get_all_episodes(found['result']['tvshows'][0])
		except:
			return "Nothing found for '{}'.".format(q)

	def list_shows(self, andprint=True):
		# Returns the list of TV shows (and prints them)
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
			"params":{
				"properties": ["title", "file", "playcount"],
				"sort": {"order": "ascending", "method": "label", "ignorearticle": True}
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		if andprint:
			print("Listing TV shows.\n---")
		try:
			for tv in found['result']['tvshows']:
				if andprint:
					print(tv['title'])
			return found['result']['tvshows']
		except:
			return []
	def list_movies(self, andprint=True):
		# Returns the list of movies (and prints them)
		if andprint:
			print("Listing movies.\n---")
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies",
			"params":{
				"properties": ["title", "file", "playcount"],
				"sort": {"order": "ascending", "method": "label", "ignorearticle": True}
			},
			"id": "libMovies"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		try:
			for mov in found['result']['movies']:
				if andprint:
					print(mov['title'])
			return found['result']['movies']
		except:
			return []
	def __movielist(self, q):
		# Returns the list of movies (to automatically play)
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies",
			"params":{
				"filter": {"field":"title", "operator":"contains", "value": q},
				"properties": ["title", "file", "playcount"],
				"sort": {"order": "ascending", "method": "label", "ignorearticle": True}
			},
			"id": "libMovies"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		try:
			return found['result']['movies'][0]
		except:
			return None

	def __is_special(self, q):
		for special in self.specials:
			if q in special: return special[q]
		return False

	def find_from(self, content, q):
		# Look for a title in the lists of TV shows or movies
		special = self.__is_special(q)
		if special: q = special
		print("Looking for '{}' in {}...".format(q, content.upper()))
		matched = "Couldn't find '{}'.".format(q)
		if 'movie' in content:
			movies = self.list_movies(0)
			for mov in  movies:
				if q.lower() in mov['title'].lower():
					print(mov['title'])
					matched = ''
		else:
			return self.list_episodes(q)
			shows = self.list_shows(0)
			for tv in  shows:
				if q.lower() in tv['title'].lower():
					print(tv['title'])
					matched = ''
		print(matched)
	def __tvlist(self, q):
		# Returns the list of TV shows for automatic playback
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
			"params":{
				"filter": {
					"and":[
						{"field":"title", "operator":"contains", "value": q},
						{"field":"playcount", "operator":"is", "value": "0"}
					]
				},
				"properties": ["title", "file", "playcount"],
				"sort": {"order": "ascending", "method": "label", "ignorearticle": True}
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		print("Looking for '{}'...".format(q))
		try:
			return found['result']['tvshows'][0]
		except:
			return None

	def search_episodes(self, epnum):
		# Get a specific episode, even if it's been watched
		if not re.search('[a-z0-9_\-] \- \d+x\d\d', epnum):
			return "Please format the show/episode as: 'Show Name - 1x01'"
		show = epnum.split(' - ')[0].strip()
		special = self.__is_special(show)
		if special: show = special
		print("Looking for '{}'...".format(show))
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
			"params":{
				"filter": {"field":"title", "operator":"contains", "value": show},
				"properties": ["title", "file"],
				"sort": {"order": "ascending", "method": "label", "ignorearticle": True}
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		try:
			print("Found '{}'".format(found['result']['tvshows'][0]['title']))
			return self.__get_old_episode(epnum, found['result']['tvshows'][0])
		except:
			return "Couldn't find the show '{}'".format(show)
	def __get_all_episodes(self, show):
		# Get a list of episodes for a specific show
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
			"params": {
				"tvshowid": show["tvshowid"],
				"properties": ["title", "file", "playcount"]
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads(results)
		try:
			print(show['title'] + '\n----------')
			for episode in found['result']['episodes']:
				print(episode['label'])
		except:
			return "No episodes for '{}'".format(show['title'])
		return ''

	def __get_next_episode(self, show):
		# Play the next unwatched episode of a TV show.
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
			"params":{
				"tvshowid": show['tvshowid'],
				"properties": ["title", "file", "playcount"],
				"filter": {"field":"playcount", "operator":"is", "value": "0"}
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		print('Getting next episode...')
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		episode = found['result']['episodes'][0]
		matched = self.__begin(episode)
		return matched

	def __pick_episode(self, epnum, episodes):
		# Return a specific episode using the format SxEE.
		for episode in episodes:
			if epnum in episode['label']:
				print("Found '{}'".format(episode['label']))
				return episode
		return None

	def __get_old_episode(self, epnum, show):
		# Start playing a specific episode using the format SxEE.
		epnum = epnum.split(' - ')[1].strip()
		params = {
			"jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
			"params":{
				"tvshowid": show['tvshowid'],
				"properties": ["title", "file", "playcount"]
			},
			"id": "libTvShows"
		}
		cmd = json.dumps(params)
		print("Looking for episode '{}'...".format(epnum))
		results = simplecurl.get_contents(self.url + cmd)
		found = json.loads( results )
		try:
			episode = self.__pick_episode(epnum, found['result']['episodes'])
			return self.__begin(episode)
		except:
			return "Couldn't find episode '{}: {}'.".format(show['title'], epnum)

	def search_movies(self, moviename):
		# Find, and play a specific movie
		movie = self.__movielist(moviename)
		if movie:
			matched = "Found '" + movie['title'] + "'\n"
			matched = matched + self.__begin(movie)
		else:
			matched = "No matches found for '{}'".format(moviename)
		return matched

	def search_shows(self, showname):
		# Find, and play the next unwatched episode of a TV show
		special = self.__is_special(showname)
		if special: showname = special
		show = self.__tvlist(showname)
		if show:
			playstr = 'Playing {}: '.format(show['title'])
			matched = self.__get_next_episode(show)
			matched = re.sub('Playing', playstr, matched)
		else:
			matched = "No unwatched episodes for '{}'".format(showname)
		return matched
