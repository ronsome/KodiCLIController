An API and command line interface for controlling Kodi.

## Commands

- `--play`, `-p`                  Resume playback.
- `--pause`                       Pause playback.
- `--stop`, `-s`                    Stop playback.
- `--find-movie [title]`          Play a movie with the specified title.
- `--find-epiode`, `-e [title]`   Play a sepcific TV episode.
- `--list-movies`                 List movies.
- `--list-shows`                  List TV shows.
- `--scan`, `-u`                  Scan and update the video library.
- `--help`, `-h`                  Display this help file.
- `--version`, `-v`               Display Kodi-Control version and about.

  kodi --find-movie 'The Avengers'
  kodi --find-episode 'Arrow - 3x04'

To get a list of movies or TV shows based on a search term, use:

    kodi --find-movies 'The Avengers'
  
    kodi --find-show Suits
