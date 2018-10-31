import asyncio
from datetime import datetime

import reddit
from playlist import Playlist


def refresh_playlist(event, context):
    """
    AWS Lambda function
    """
    print("Updating Listen With Reddit playlist at {}...".format(event["time"]))
    loop = asyncio.get_event_loop()
    playlist = Playlist()
    try:
        tracks = loop.run_until_complete(reddit.request())
        success = loop.run_until_complete(playlist(tracks))

        if not success:
            raise Exception("Error updating playlist")
    except:
        print("Refresh failed")
        raise
    else:
        print("Refresh passed!")
        return event["time"]
    finally:
        print("Refresh complete at {}".format(str(datetime.now())))
        loop.close()
