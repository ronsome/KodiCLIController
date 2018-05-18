#!/usr/bin/python
# kodi/control.py
# Ron Newsome, Jr. <http://ronsome.net/>
# 2018-04-09

import sys, re, command

def unknown_command(cmd):
	print( "[{}] is not a valid command.".format(cmd.upper()) )
	print("Try 'kodi help' for a list of valid commands.")

version = '0.4'
video = None
try:
	cmd = sys.argv[1]
	if len(sys.argv) > 2:
		video = sys.argv[2]
except:
	cmd = input('Enter a command [play/pause, stop, or info]: ')

cmd = cmd.lower()
try:
	player = command.Player()
except:
	player = None

version_info = '''
     Kodi-Control v. {}
 (c) 2018 Ron Newsome Jr.
   <http://ronsome.net>
           ---
A simple program to control 
the Kodi media player.
'''.format(version)

help_contents = '''
----* KODI-CONTROL HELP *----
CMD                         Description
========                    ==================
PLAY, -c                    Continue playback.
PAUSE, -w                   Pause playback.
TOGGLE, -p                  Toggle between play and pause.
STOP, -s                    Stop playback.
INFO, -i                    Display on-screen info.
MOVIE, -m [title]           Play a movie.
TV, -t [title]              Specify a TV show and play 
                              the next unwatched episode.
EPISODE, -e [title]         Find and play a sepcific TV episode.
FIND, -f [content:title]    Find movies or TV shows.
LIST, -l [type]             List movies or TV shows.
SCAN, -u                    Scan and update the video library.
HELP, -h                    Display this help file.
ABOUT, -v                   Display Kodi-Control version and about.

MOVIE, TV, and EPISODE commands can optionally specify the show or movie
you want to play:
    kodi movie 'The Avengers'
    kodi -t 'Game of Thrones'
    kodi -e 'Arrow - 3x04'

To get a list of movies or TV shows based on a search term, use:
    kodi find 'movies:The Avengers'
    kodi -fm 'The Avengers'
    kodi find tv:Suits
    kodi -ft Suits
'''

short_commands = {
	'-c':   'play',
	'-e':   'episode',
	'-f':   'find',
	'-fm':  'find-movie',
	'-ft':  'ftv',
	'-ftv': 'ftv',
	'-h':   'help', '--help':'help',
	'-hs':  'home',
	'-i':   'info',
	'-l':   'list',
	'-m':   'movie',
	'-p':   'toggle',
	'-s':   'stop',
	'-t':   'tv',
	'-u':   'scan',
	'-v':   'about',
	'-w':   'pause'
}

if '-' in cmd:
	if '--' in cmd:
		cmd = cmd.replace('--', '')
	else:
		try:
			cmd = short_commands[cmd]
		except:
			unknown_command(cmd)
			exit()

if cmd == 'help':
	print(help_contents)
	exit()
elif (cmd == 'about') | (cmd == 'version'):
	print(version_info)
	exit()
elif not player:
	print("Kodi is not available.")
	exit()
elif cmd == 'toggle': print( player.play_pause() )
elif cmd == 'play':
	if not player.is_playing():
		print(player.play_pause() )
	else:
		print('Kodi is not paused.')
elif cmd == 'pause':
	if player.is_playing():
		print(player.play_pause() )
	else:
		print('Kodi is not playing.')

elif cmd == 'home': player.to_home_screen()
elif (cmd == 'scan') | (cmd == 'update'): print( player.scan() )
elif cmd == 'stop': print( player.stop() )
elif cmd == 'info': print( player.display_info() )
elif cmd == 'status': print( player.display_info() )
elif cmd == '-lm': player.list_movies()
elif cmd == '-lt': player.list_movies()
elif cmd == 'list': 
	if not video:
		video = input("List movies or TV shows? [MOVIES/TV] ")
	if 'movie' in video.lower():
		player.list_movies()
	if 'tv' in video.lower():
		player.list_shows()
	exit()
elif 'find-movie' in cmd: player.find_from('movies', video)
elif cmd == 'find-tv': player.find_from('tv', video)
elif cmd == 'ftv': print( player.find_from('tv', video) )
elif cmd == 'find':
	if not video:
		video = input("What do you want to find? ")
	query = video.lower().split(':')
	content = query[0]
	term = query[1].strip()
	if re.search('tv:|movie:', video, re.I):
		player.find_from(content, term)
elif 'movie' in cmd:
	if video:
		q = video
	else:
		q = input('Enter the movie to search for: ')
	if len(q):
		print( player.search_movies(q) )
elif (cmd == 'tv') | ('show' in cmd):
	if video:
		q = video
	else:
		q = input('Enter the show to search for: ')
	if len(q):
		print( player.search_shows(q) )
elif 'episode' in cmd:
	if video:
		q = video
	else:
		q = input('Enter the episode to search for: ')
	if len(q):
		print( player.search_episodes(q) )

else: 
	unknown_command(cmd)