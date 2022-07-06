import subprocess

from pyyoutube import Api
import config


"""Библиотека для скачивания комментов в файл"""
import youtube_comment_downloader


api = Api(api_key=config.youtube_dev_api_key)

"""С ютуб апи"""
def scrap_comments(video_id: str) -> []:
    comments = api.get_comment_threads(parts=['snippet', 'replies'], video_id=video_id, count=2500)
    arr = []
    for i in comments.items:
        comm = i.snippet.topLevelComment.snippet.textOriginal
        arr.append(comm)
    return arr




def scrap_comments_new(video_id: str):
    """Запуск с консоли"""
    subprocess.check_output(f'youtube-comment-downloader --url {video_id} --output README.md', shell=True)
