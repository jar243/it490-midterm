import json

import requests
from pydantic import BaseSettings, BaseModel

from broker import UserError, run_rabbit_app
from youtube import YoutubeDataApi


class EnvConfig(BaseSettings):
    broker_host: str = "127.0.0.1"
    broker_port: int = 5672
    broker_user: str = "guest"
    broker_password: str = "guest"
    tmdb_api_key: str
    youtube_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_prefix = "IT490_"


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
            "runtime": raw_movie.get("runtime", 2 * 60) * 60,
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


youtube_api: YoutubeDataApi


class YoutubeMovieReq(BaseModel):
    movie_title: str


def handle_get_youtube_movie(req_body: dict):
    req = YoutubeMovieReq(**req_body)
    search_result = youtube_api.search_movie(req.movie_title)
    if search_result is None:
        raise UserError("Movie is not available on Youtube Movies")
    details = youtube_api.get_video_details(search_result.video_id)
    if details is None:
        raise UserError("Movie is not available on Youtube Movies")
    return {
        "youtube_id": search_result.video_id,
        "youtube_length": details.duration_sec,
    }


def main():
    routes = {
        "api.movies.get": handle_movies_get,
        "api.movies.search": handle_movies_search,
        "api.trending.movies": handle_trending_movies,
        "api.popular.movies": handle_popular_movies,
        "api.youtube.get-movie": handle_get_youtube_movie,
    }

    config = EnvConfig()

    global api
    api = MoviesApi(config.tmdb_api_key)

    global youtube_api
    youtube_api = YoutubeDataApi(config.youtube_api_key)

    run_rabbit_app(
        "dmz",
        config.broker_host,
        config.broker_port,
        config.broker_user,
        config.broker_password,
        routes,
    )


if __name__ == "__main__":
    main()
