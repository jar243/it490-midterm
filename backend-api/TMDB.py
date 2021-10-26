import requests
import tmdbsimple as tmdb
import pprint
from api_data import API_KEY

tmdb.API_KEY = API_KEY

def search_movies (movie_name: str):
    search = tmdb.Search()
    movie_name = input("Movie Name:")
    response = search.movie(query= movie_name)
 
    for s in search.results:
        print(s['title'], s['id'], s['release_date'])

    return[]

search_movies(movie_name=input("Movie Name:"))
""""
def discover_movies(year: int):
    discover = tmdb.Discover()
    year = year
    response = discover.movie(query= year)
    for s in discover.results:
        print(s['title'], s['release_date'])
    
    return[]
"""""
#discover_movies(year=input("Year: "))










