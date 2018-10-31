import os
import json
import asyncio

from aiohttp import ClientSession, BasicAuth

import reddit


class Playlist:
    def __init__(self):
        self.user = "1281866745"
        self.api = "https://api.spotify.com/v1"
        self.playlist = "5oXDb1n86jxFpJiLvKYyFH"

    def authenticate(func):
        async def wrapper(self, *args):
            client = os.environ["SCLIENT"]
            secret = os.environ["SSECRET"]
            refresh = os.environ["REFRESH_TOKEN"]
            url = "https://accounts.spotify.com/api/token"

            auth = BasicAuth(client, secret)
            data = {"grant_type": "refresh_token", "refresh_token": refresh}

            async with ClientSession(auth=auth) as session:
                async with session.post(url, auth=auth, data=data) as response:
                    response = await response.json()
                    self.token = "Bearer " + response["access_token"]
                    self.headers = {"Authorization": self.token}
            return await func(self, *args)

        return wrapper

    async def _request(self, url, data=None, method=None):
        method = getattr(self.session, method)
        async with method(url, data=data) as response:
            return await response.json()

    @authenticate
    async def __call__(self, tracks):
        self.tracks = tracks
        async with ClientSession(headers=self.headers) as self.session:
            return await self.generate_playlist()

    async def generate_playlist(self):
        try:
            await self.search_for_tracks()
            await self.replace_playlist_tracks()
            return True
        except:
            return False

    async def search_for_tracks(self):
        tasks = (asyncio.ensure_future(self.find_track(track)) for track in self.tracks)
        tracks = await asyncio.gather(*tasks)
        self.tracks = {track for track in tracks if track is not None}
        print(f"{len(self.tracks)} tracks were found")

    async def find_track(self, track):
        url = f"{self.api}/search?q={track}&type=track"
        response = await self._request(url, method="get")
        found = response.get("tracks", None)

        if found and found["total"]:
            raw_track = response["tracks"]["items"][0]
            song = "spotify:track:" + raw_track["id"]
            return song

    async def replace_playlist_tracks(self):
        url = f"{self.api}/playlists/{self.playlist}/tracks"
        data = {"uris": list(self.tracks)}
        data = json.dumps(data)
        response = await self._request(url, data=data, method="put")

        if response["snapshot_id"]:
            print("Tracks succesfully added to playlist")

    async def create_playlist(self, name):
        url = f"{self.api}/users/{self.user}/playlists"
        data = json.dumps({"name": name})
        response = await self._request(url, data=data, method="post")
        name = response.get("name", None)
        if name:
            return True
        return False

    async def get_playlist(self):
        url = f"{self.api}/playlists/{self.playlist}"
        response = await self._request(url, method="get")
        playlist_url = response["external_urls"]["spotify"]
        print(playlist_url)

    async def get_playlists(self):
        url = f"{self.api}/me/playlists"
        response = await self._request(url, method="get")
        for playlist in response["items"]:
            print(playlist["name"], playlist["id"])
