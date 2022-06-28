import pyyoutube
import numpy as np
from pyyoutube import Api
import config
api = Api(api_key=config.youtube_dev_api_key)


def scrap_comments(video_id: str) -> []:
    comments = api.get_comment_threads(parts=['snippet', 'replies'], video_id=video_id, count=9999999999)
    arr = []
    for i in comments.items:
        comm = i.snippet.topLevelComment.snippet.textDisplay
        arr.append(comm)
    return arr
