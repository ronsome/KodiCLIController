Command line interface for controlling Kodi.

CMD                         Description

---

- PLAY, -c                    Continue playback.
- PAUSE, -w                   Pause playback.
- TOGGLE, -p                  Toggle between play and pause.
- STOP, -s                    Stop playback.
- INFO, -i                    Display on-screen info.
- MOVIE, -m [title]           Play a movie.
- TV, -t [title]              Specify a TV show and play the next unwatched episode.
- EPISODE, -e [title]         Find and play a sepcific TV episode.
- FIND, -f [content:title]    Find movies or TV shows.
- LIST, -l [type]             List movies or TV shows.
- SCAN, -u                    Scan and update the video library.
- HELP, -h                    Display this help file.
- ABOUT, -v                   Display Kodi-Control version and about.

MOVIE, TV, and EPISODE commands can optionally specify the show or movie
you want to play:

- kodi movie 'The Avengers'
- kodi -t 'Game of Thrones'
- kodi -e 'Arrow - 3x04'

To get a list of movies or TV shows based on a search term, use:

- kodi find 'movies:The Avengers'
- kodi -fm 'The Avengers'
- kodi find tv:Suits
- kodi -ft Suits