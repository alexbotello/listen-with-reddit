import os
import re
import asyncio

from aiohttp import ClientSession, BasicAuth

subreddits = ("Music", "listentothis")


async def request():
    url = "https://oauth.reddit.com/r/"
    paths = (
        f"{url}{subreddit}/top?t=day&limit=30"  # Top submissions past 24 hours
        for subreddit in subreddits
    )
    token = await authenticate()
    headers = {"Authorization": token}

    async with ClientSession(headers=headers) as session:
        tasks = (
            asyncio.ensure_future(get_subreddit_posts(path, session)) for path in paths
        )
        results = await asyncio.gather(*tasks)
    return parse(results)


async def authenticate():
    client = os.environ["RCLIENT"]
    secret = os.environ["RSECRET"]
    url = "https://www.reddit.com/api/v1/access_token"

    auth = BasicAuth(client, secret)
    data = {"grant_type": "client_credentials"}

    async with ClientSession(auth=auth) as session:
        async with session.post(url, auth=auth, data=data) as response:
            response = await response.json()
            token = "Bearer " + response["access_token"]
            return token


async def get_subreddit_posts(url, session):
    async with session.get(url) as response:
        response = await response.json()
        posts = response["data"]["children"]
        return (post["data"]["title"] for post in posts)


def parse(subreddits):
    matches = (
        re.search("\[(.*)\]", post, flags=re.I)
        for subreddit in subreddits
        for post in subreddit
    )
    raw_titles = (match.string for match in matches if match is not None)

    return (
        title.split("[")[0].split("(")[0].replace("-", "", 3) for title in raw_titles
    )
