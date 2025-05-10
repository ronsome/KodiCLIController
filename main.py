#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""A simple program to control the Kodi media player."""

import argparse
import kodiapi

__author__     = "Ron Newsome, Jr."
__copyright__  = "Copyright 2018, Ron Newsome, Jr."
__version__    = "0.5.1"
__maintainer__ = "Ron Newsome, Jr."
__license__    = "GPL-3.0"
__status__     = "Development"
__updated__    = "2025-05-10"

help_contents = '''
----* KODI-CONTROL HELP *----
MOVIE, TV, and EPISODE commands can optionally specify the show or movie
you want to play:
    kodi movie 'The Avengers'
    kodi -t 'Game of Thrones'
    kodi -e 'Arrow - 3x04'

To get a list of movies or TV shows based on a search term, use:
    kodi --find 'movies:The Avengers'
    kodi --fm 'The Avengers'
    kodi --find 'tv:Suits'
    kodi --ft Suits
'''

def version_info():
  print(f'''
     Kodi-Control v. {__version__}
 (c) 2018 Ron Newsome Jr.
   <http://ronsome.net>
           ---
A simple program to control
   the Kodi media player.
''')

def main():
  player = kodiapi.Player()
  if not player.connected:
    return pint('Kodi was not detected.')

  parser = argparse.ArgumentParser(help_contents)
  parser.add_argument("--episodes", type=str, help="List episodes for given show")
  parser.add_argument("--find-episode", type=str, help="Find & play an episode")
  parser.add_argument("--find-movie", type=str, help="Find & play a movie")
  parser.add_argument("--movies", action='store_true', help='List available movies')
  parser.add_argument("--pause", action='store_true', help='Pause')
  parser.add_argument("--play", action='store_true', help='Resume playing')
  parser.add_argument("-u", "--scan", action='store_true', help='Scan video library')
  parser.add_argument("--shows", action='store_true', help='List available TV shows')
  parser.add_argument("--stop", action='store_true', help='Stop')
  parser.add_argument("-v", "--version", action='store_true', help='Stop')
  args = parser.parse_args()

  if args.episodes:
    return [print(i['label']) for i in player.list_episodes(args.episodes)]
  if args.find_episode: return print( player.play_episode(args.find_episode) )
  if args.find_movie: return print( player.play_movie(args.find_movie) )
  if args.movies:
    return [print(i['label']) for i in player.list_movies()]
  if args.pause: return print( player.play_pause() )
  if args.play: return print( player.play_pause() )
  if args.scan: return print( player.scan() )
  if args.shows:
    return [print(i['label']) for i in player.list_shows()]
  if args.stop: return print( player.stop() )
  if args.version: return version_info()

if __name__ == '__main__':
  main()
