import requests
import json

from pydantic import BaseSettings
from broker import run_rabbit_app, UserError


class EnvConfig(BaseSettings):
    tmdb_api_key: str = "291050bd6f830358af2856e014e9dec6"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class MoviesApi:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._host_url = "https://api.themoviedb.org"
        self._image_url = "https://image.tmdb.org/t/p/w500/"

    def _format_movie_data(self, raw_movie: dict):
        return {
            "id": raw_movie["id"],
            "title": raw_movie["title"],
            "description": raw_movie["overview"],
            # "genre_ids": raw_movie["genre_ids"],
            "year": raw_movie.get("release_date", "0000")[:4],
            "poster_url": f"{self._image_url}{raw_movie['poster_path'][1:]}",
        }

    def _format_many_movies(self, raw_movies: list[dict]):
        return [
            self._format_movie_data(movie)
            for movie in raw_movies
            if movie["poster_path"] is not None
        ]

    def search_movies(self, search_str: str):
        api_search = f"{self._host_url}/3/search/movie?api_key={self._api_key}"
        params = {"query": search_str}
        response = requests.get(api_search, params)

        if response.status_code == 200:
            data = json.loads(response.text)
            return self._format_many_movies(data["results"])
        else:
            raise RuntimeError(f"API Error: {response.status_code}")

    def get_movie(self, movie_id: str):
        path = f"{self._host_url}/3/movie/{movie_id}?api_key={self._api_key}"
        res = requests.get(path)
        if res.status_code == 200:
            return self._format_movie_data(json.loads(res.text))
        elif res.status_code == 404:
            raise UserError(f"Movies ID does not exist: {movie_id}")
        else:
            raise RuntimeError(f"API Error: {res.status_code}")

    def trending_movies(self):
        path = f"{self._host_url}/3/trending/movie/week?api_key={self._api_key}"
        response = requests.get(path)

        if response.status_code == 200:
            data = json.loads(response.text)
            return self._format_many_movies(data["results"])
        else:
            raise RuntimeError(f"API Error: {response.status_code}")

    def popular_movies(self):
        path = f"{self._host_url}/3/movie/popular?api_key={self._api_key}"
        response = requests.get(path)

        if response.status_code == 200:
            data = json.loads(response.text)
            return self._format_many_movies(data["results"])
        else:
            raise RuntimeError(f"API Error: {response.status_code}")


api: MoviesApi


def handle_movies_get(req_body: dict):
    movie_id = req_body.get("movie_id")
    if movie_id is None or not isinstance(movie_id, str) or len(movie_id) == 0:
        raise ValueError("Invalid movie_id supplied")
    return api.get_movie(movie_id)


def handle_movies_search(req_body: dict):
    query = req_body.get("query")
    if query is None or not isinstance(query, str) or len(query) == 0:
        raise ValueError("Invalid query supplied")

    results = api.search_movies(query)
    return {"movies": results}


def handle_trending_movies(req_body: dict):
    results = api.trending_movies()
    return {"movies": results}


def handle_popular_movies(req_body: dict):
    results = api.popular_movies()
    return {"movies": results}


def main():
    routes = {
        "api.movies.get": handle_movies_get,
        "api.movies.search": handle_movies_search,
        "api.trending.movies": handle_trending_movies,
        "api.popular.movies": handle_popular_movies,
    }

    global api
    config = EnvConfig()
    api = MoviesApi(config.tmdb_api_key)

    run_rabbit_app("backend-api", "127.0.0.1", 5672, "guest", "guest", routes)


if __name__ == "__main__":
    main()
