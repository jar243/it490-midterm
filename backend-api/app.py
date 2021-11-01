import requests
import json
import pprint
from pydantic import BaseSettings



class EnvConfig(BaseSettings):
    tmdb_api_key: str

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'



class MoviesApi:
    def __init__(self, api_key:str):
        self._api_key = api_key
        self._base_url = 'https://api.themoviedb.org'

    def search_movies(self, search_str: str):
        # logic here
        search_str = input("Search Movie: ")
        api_search = f"{self._base_url}/3/search/movie?api_key={self._api_key}"
        params = {'query':search_str}

        response = requests.get(api_search, params)

        # request data and check for error 
        if response.status_code == 200:
            data = json.loads(response.text)
            for i in data['results']:
                print('Title: ' + i['title'] +'\n')
                print('Overview: ' + i['overview']+'\n')
                print(i['backdrop_path'])

        else:
            print(f" Error: {response.status_code} ")
        return []

    def trending_movies(self):

        movies_trending = "https://api.themoviedb.org/3/trending/movie/week?api_key=" + self._api_key
        response = requests.get(movies_trending)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Title: ' + i['title'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                print(i['backdrop_path'])

        else:
            print(f"Error: {response.status_code} ")
        return[]

    def trending_shows(self):
    
        shows_trending = "https://api.themoviedb.org/3/trending/tv/week?api_key=" + self._api_key
        response = requests.get(shows_trending)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Name: ' + i['name'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                print(i['backdrop_path'])

        else:
            print(f"Error: {response.status_code} ")
        return[]

    def popular_movies(self):
        popular = "https://api.themoviedb.org/3/movie/popular?api_key=" + self._api_key
        response = requests.get(popular)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Title: ' + i['title'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                print(i['backdrop_path'])

        else:
            print(f"Error: {response.status_code} ")
        return[]

    def popular_shows(self):
        popular = "https://api.themoviedb.org/3/tv/popular?api_key=" + self._api_key
        response = requests.get(popular)

        if response.status_code == 200:
            data = json.loads(response.text)
            
            for i in data['results']:
                print('Name: ' + i['name'] + '\n')
                print('Overview: ' + i['overview']+'\n')
                print(i['backdrop_path'])

        else:
            print(f"Error: {response.status_code} ")
        return[]


config = EnvConfig()
api = MoviesApi(config.tmdb_api_key)

#search_movie.search_movies("")

trending = api.trending_shows()
print(trending)

popular = api.popular_shows()
print(popular)
