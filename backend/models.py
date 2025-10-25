from datetime import datetime

class Movie:
    def __init__(self, tmdb_id, title, description, genre, rating, 
                 duration, poster, year):
        self.tmdb_id = tmdb_id
        self.title = title
        self.description = description
        self.genre = genre
        self.rating = rating
        self.duration = duration
        self.poster = poster
        self.year = year
        self.links = []
        self.created_at = datetime.now()

class Series:
    def __init__(self, tmdb_id, title, description, genre, rating, 
                 poster, year, seasons=1):
        self.tmdb_id = tmdb_id
        self.title = title
        self.description = description
        self.genre = genre
        self.rating = rating
        self.poster = poster
        self.year = year
        self.seasons = seasons
        self.links = []
        self.created_at = datetime.now()

class Link:
    def __init__(self, content_id, content_type, url, source, 
                 season=None, episode=None):
        self.content_id = content_id
        self.content_type = content_type  # 'movie' o 'series'
        self.url = url
        self.source = source  # 'pelisplushd', 'pelicinehd', etc
        self.season = season
        self.episode = episode
        self.language = language
        self.status = 'active'
        self.scraped_at = datetime.now()
        self.checked_at = None
