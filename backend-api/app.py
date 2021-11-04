import requests
import json

from pydantic import BaseSettings
from broker import run_rabbit_app

class EnvConfig(BaseSettings):
    tmdb_api_key: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

class MoviesApi:
    def __init__(self, api_key:str):
        self._api_key = api_key
        self._host_url = 'https://api.themoviedb.org'
        self._image_url = 'https://image.tmdb.org/t/p/w500/'

    def search_movies(self, search_str: str):
        # logic here
        search_str = input("Search Movie: ")
        api_search = f"{self._host_url}/3/search/movie?api_key={self._api_key}"
        params = {'query':search_str}

        response = requests.get(api_search, params)

        # request data and check for error 
        if response.status_code == 200:
            data = json.loads(response.text)
            for i in data['results']:
                print('Title: ' + i['title'] +'\n')
                print('Overview: ' + i['overview']+'\n')
                poster_path = (i['backdrop_path'])
                if poster_path != None:
                    print(f"{self._image_url}{poster_path}")
                else:
                    print("Sorry, poster not available")

        else:
            print(f" Error: {response.status_code} ")
        return []

    def trending_movies(self):

        movies_trending = f"{self._host_url}/3/trending/movie/week?api_key=" + self._api_key
        response = requests.get(movies_trending)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Title: ' + i['title'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                poster_path = (i['backdrop_path'])
                if poster_path != None:
                    print(f"{self._image_url}{poster_path}")
                else:
                    print("Sorry, poster not available")

        else:
            print(f"Error: {response.status_code} ")

        
        return[]

    def trending_shows(self):
    
        shows_trending = f"{self._host_url}/3/trending/tv/week?api_key=" + self._api_key
        response = requests.get(shows_trending)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Name: ' + i['name'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                poster_path = (i['backdrop_path'])
                if poster_path != None:
                    print(f"{self._image_url}{poster_path}")
                else:
                    print("Sorry, poster not available")

        else:
            print(f"Error: {response.status_code} ")
        return[]

    def popular_movies(self):
        popular = f"{self._host_url}/3/movie/popular?api_key=" + self._api_key
        response = requests.get(popular)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Title: ' + i['title'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                poster_path = (i['backdrop_path'])
                if poster_path != None:
                    print(f"{self._image_url}{poster_path}")
                else:
                    print("Sorry, poster not available")

        else:
            print(f"Error: {response.status_code} ")
        return[]

    def popular_shows(self):
        popular = f"{self._host_url}/3/tv/popular?api_key=" + self._api_key
        response = requests.get(popular)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Name: ' + i['name'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                poster_path = (i['backdrop_path'])
                if poster_path != None:
                    print(f"{self._image_url}{poster_path}")
                else:
                    print("Sorry, poster not available")
        else:
            print(f"Error: {response.status_code} ")
        return[]


api: MoviesApi

def handle_movies_search(req_body: dict):
    query = req_body.get('query')
    if query is None or not isinstance(query, str) or len(query) == 0:
        raise RuntimeError('Invalid query supplied')

    results = []

    return {'results': results}

def handle_trending_movies(req_body: dict):
    results = []
    return {'results': results}

def handle_trending_shows(req_body: dict):
    results = []
    return {'results': results}

def handle_popular_movies(req_body: dict):
    results = []
    return {'results' : results}

def handle_popular_shows(req_body: dict):
    results = []
    return {'results' : results}

def main():

    search_routes = {
        'api.movies.search': handle_movies_search     
    }

    trending_movies = {
        'api.trending.movies' : handle_trending_movies
    }
    trending_shows = {
        'api.trending.shows' : handle_trending_shows
    }
    popular_movies = {
        'api.popular.movies' : handle_popular_movies
    }
    popular_shows = {
        'api.popular.shows' : handle_popular_shows
    }
    global api
    config = EnvConfig()
    api = MoviesApi(config.tmdb_api_key)

    run_rabbit_app('backend-api', '127.0.0.1', 5672, 'guest', 'guest', search_routes,trending_movies,trending_shows,popular_shows,popular_movies)

