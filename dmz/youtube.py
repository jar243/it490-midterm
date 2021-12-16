import json
import math
from dataclasses import dataclass
from typing import Union

import requests


@dataclass
class SearchResult:
    video_id: str
    video_title: str
    video_description: str
    channel_id: str
    channel_title: str

    @property
    def url(self):
        return f"https://youtu.be/{self.video_id}"


@dataclass
class VideoDetails:
    duration_sec: int


class YoutubeDataApi:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._movies_channel_id = "UClgRkhTL3_hImCAmdLfDE4g"
        self._base_url = "https://www.googleapis.com/youtube/v3"

    def _gen_url(self, url_route: list[str]):
        return f"{self._base_url}/{'/'.join(url_route)}"

    def _get(self, url_route: Union[str, list[str]], params: dict[str, str] = {}):
        params["key"] = self._api_key
        url = self._gen_url([url_route] if isinstance(url_route, str) else url_route)
        return requests.get(url, params)

    def search_movie(self, query: str):
        params = {
            "q": query,
            "part": "id,snippet",
            "type": "video",
            "videoType": "movie",
            "safeSearch": "none",
            "order": "relevance",
            "maxResults": "10",
        }
        res = self._get("search", params)
        if res.status_code != 200:
            raise RuntimeError(f"Status {res.status_code}: {res.reason}")
        res_obj = json.loads(res.content)
        results: list[SearchResult] = []
        for result_item in res_obj["items"]:
            snippet = result_item["snippet"]
            results.append(
                SearchResult(
                    video_id=result_item["id"]["videoId"],
                    video_title=snippet["title"],
                    video_description=snippet["description"],
                    channel_id=snippet["channelId"],
                    channel_title=snippet["channelTitle"],
                )
            )
        if len(results) == 0:
            return None
        result = results[0]
        for movie in results:
            if movie.channel_id == self._movies_channel_id:
                result = movie
        if result.video_title.lower() != query.lower():
            return None
        return result

    def get_video_details(self, video_id: str):
        # YouTube does not let u access length of movies :((
        # Responding with a default value of 3 hours
        return VideoDetails(3 * 60 * 60)
        params = {
            "id": video_id,
            "part": "fileDetails",
        }
        res = self._get("videos", params)
        if res.status_code != 200:
            raise RuntimeError(f"Status {res.status_code}: {res.reason}")
        res_obj = json.loads(res.content)
        videos: list = res_obj["items"]
        if len(videos) == 0:
            return None
        video = videos[0]
        duration_sec = math.trunc(video["fileDetails"]["durationMs"] / 1000)
