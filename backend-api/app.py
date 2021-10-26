import requests
import json
import pprint
from requests import api
from api_data import API_KEY, API_HOST

api_key = API_KEY
api_host = API_HOST

class MoviesApi:

    def search_movies(self, search_str: str):
        # logic here
        search_str = input("Search Movie: ")
        api_search = "https://api.themoviedb.org/3/search/movie?api_key="+ api_key
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

        movies_trending = "https://api.themoviedb.org/3/trending/movie/week?api_key=" + api_key
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
    
        shows_trending = "https://api.themoviedb.org/3/trending/tv/week?api_key=" + api_key
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
        popular = "https://api.themoviedb.org/3/movie/popular?api_key=" + api_key
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
        popular = "https://api.themoviedb.org/3/tv/popular?api_key=" + api_key
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
"""
search_movie = MoviesApi()
#search_movie.search_movies("")

trending = MoviesApi()
all = trending.trending_shows()
print(all)
"""
popular = MoviesApi()
pop = popular.popular_shows()
print(pop)
