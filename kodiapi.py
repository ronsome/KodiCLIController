#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""An API for interfacing with the Kodi media player JSON-RPC API."""

import json
import re
import requests

__author__     = "Ron Newsome, Jr."
__copyright__  = "Copyright 2018, Ron Newsome, Jr."
__version__    = "0.5.1"
__maintainer__ = "Ron Newsome, Jr."
__license__    = "GPL-3.0"
__status__     = "Development"
__updated__    = "2025-05-10"

CONFIG = {
# Change this to your Kodi machine's IP address
  'ip_address': 'localhost',

# The default port is 8080
  'port': 8080,

# Change this to your Kodi username
  'username': 'kodi',

# Change this to your Kodi password
  'password': 'abc',
}

class Player:
  def __init__(self):
    global CONFIG
    self.url = f"http://{CONFIG['username']}:{CONFIG['password']}@{CONFIG['ip_address']}:{CONFIG['port']}/jsonrpc"
    self.connected = self.__detect()

  def __get_request(self, url):
    r = requests.get(url)
    return r.json()

  def __post_request(self, url, data):
    r = requests.post(url, json=data)
    return r.json()

  def __introspect(self):
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
    cmd = '?request=' + json.dumps(obj)
    return self.__get_request(self.url + cmd)

  def __detect(self):
    try:
      self.__introspect()
    except ConnectionError:
      return False
    return True

  def __begin(self, item):
    # Begin playback of an item using its "file" attribute
    # resume from where it left off, if applicable.
    params = {
      "jsonrpc":"2.0","method": "Player.Open",
      "params":{
        "item": {"file": item['file']},
        "options": {"resume": True}
      }, "id":1
    }
    playing = self.__post_request(self.url, params)
    return playing["result"] == "OK"

  def is_playing(self):
    obj = {
      "jsonrpc": "2.0", "method": "Player.GetProperties",
      "params":{
        "properties": ["speed"],
        "playerid": 1
      },
      "id": 1
    }
    cmd = '?request=' + json.dumps(obj)
    playing = self.__get_request(self.url + cmd)
    return playing['result']['speed']

  def get_whats_playing(self):
    api_params = {
      "jsonrpc": "2.0","method": "Player.GetItem",
      "params": {
        "properties": ["showtitle", "title", "season", "episode"], "playerid": 1
      },
      "id": "VideoGetItem"
    }

    jsonp = '?request=' + json.dumps(api_params)
    doc = self.__get_request(self.url + jsonp)
    resitem = doc['result']['item']
    try:
      state = '[playing]' if self.is_playing() else '[paused]'
      more = ''
      if resitem['season'] > 0 and resitem['episode'] > 0:
        more = f"{resitem['showtitle']} - {resitem['season']}x{resitem['episode']} - "
      info = f"{more}{resitem['title']} {state}"
    except:
      info = 'Nothing playing.'
    return info

  def list_shows(self):
    # Returns the list of TV shows
    params = {
      "jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
      "params":{
        "properties": ["title", "file", "playcount"],
        "sort": {"order": "ascending", "method": "label", "ignorearticle": True}
      },
      "id": "libTvShows"
    }
    cmd = '?request=' + json.dumps(params)
    found = self.__get_request(self.url + cmd)
    try:
      return found['result']['tvshows']
    except:
      pass
    return []

  def __get_show_episodes(self, show):
    # Get a list of episodes for a specific show
    params = {
      "jsonrpc": "2.0", "method": "VideoLibrary.GetEpisodes",
      "params": {
        "tvshowid": show['tvshowid'],
        "properties": ["title", "file"]
      },
      "id": "libTvShows"
    }
    cmd = '?request=' + json.dumps(params)
    found = self.__get_request(self.url + cmd)
    try:
      episodes = []
      for e in found['result']['episodes']:
        episodes.append({
          'label': f"{show['title']} - {e['label'][0:e['label'].index('.')]} - {e['title']}",
          'file': e['file']
        })
      return episodes
    except:
      pass
    return []

  def list_episodes(self, show):
    # Get a list of episodes for the given show
    params = {
      "jsonrpc": "2.0", "method": "VideoLibrary.GetTVShows",
      "params":{
        "filter": {"field":"title", "operator":"contains", "value": show},
        "properties": ["title", "file"],
        "sort": {"order": "ascending", "method": "label", "ignorearticle": True}
      },
      "id": "libTvShows"
    }
    cmd = '?request=' + json.dumps(params)
    found = self.__get_request(self.url + cmd)
    try:
      return self.__get_show_episodes(found['result']['tvshows'][0])
    except:
      return f"Couldn't find the show '{show}'"

  def list_movies(self):
    # Returns the list of movies
    params = {
      "jsonrpc": "2.0", "method": "VideoLibrary.GetMovies",
      "params":{
        "properties": ["title", "file", "playcount"],
        "sort": {"order": "ascending", "method": "label", "ignorearticle": True}
      },
      "id": "libMovies"
    }
    cmd = '?request=' + json.dumps(params)
    found = self.__get_request(self.url + cmd)
    try:
      return [{'label': m['label'], 'file': m['file']}
        for m in found['result']['movies']]
      return found['result']['movies']
    except:
      pass
    return []

  def find_movie(self, moviename):
    matched = f"Couldn't find '{moviename}'."
    movies = self.list_movies()
    matched = next((m['title'] for m in movies
      if moviename.lower() == m['title'].lower()), matched)
    return matched

  def play_pause(self):
    params = {
      "jsonrpc":"2.0","method": "Player.PlayPause",
      "params":{"playerid":1},
      "id":1
    }
    response = self.__post_request(self.url, params)
    if 'error' in response:
      return "Error during playback"

    return self.get_whats_playing()

  def stop(self):
    params = {
      "jsonrpc":"2.0","method": "Player.Stop",
      "params":{"playerid":1},
      "id":1
    }
    response = self.__post_request(self.url, params)
    if 'error' in response:
      return "Error stopping playback"

    return 'Stopping Kodi.'

  def play_movie(self, moviename):
    movies = self.list_movies()
    movie = next((m for m in movies if m['label'] == moviename), None)
    if not movie:
      return f"'{moviename}' not found."

    playing = self.__begin(movie)
    if playing:
      return f"Playing '{movie['label']}'"

    return f"Couldn't play {movie['label']}."

  def play_episode(self, show_episode):
    if not re.search(r'[a-z 0-9]+ \- \d+x\d+', show_episode, flags=re.I):
      return "Please format episode as 'Show - 1x1'"
    show, epnum = show_episode.split(' - ')
    epnum = epnum.split('x')[0] + 'x' + epnum.split('x')[-1].zfill(2)
    episodes = self.list_episodes(show)
    episode = next((e for e in episodes if epnum in e['label']), None)
    if not episode:
      return f"'{show_episode}' not found."

    playing = self.__begin(episode)
    if playing:
      return f"Playing '{episode['label']}'"

    return f"Couldn't play {episode['label']}."

  def scan(self):
    # Scan the video library only.
    params = {
      "jsonrpc":"2.0","method": "VideoLibrary.Scan", "id": 1,
      "params": {"showdialogs": True}
    }
    cmd = '?request=' + json.dumps(params)
    response = self.__get_request(self.url + cmd)
    if 'error' in response:
      return "Couldn't scan video library"

    return 'Scanning the video library'
