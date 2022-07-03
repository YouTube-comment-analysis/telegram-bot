from __future__ import print_function
import io
from comment_download import YoutubeCommentDownloader

def main():
    try:
        downloader = YoutubeCommentDownloader()
        #generator = downloader.get_comments_from_url('https://www.youtube.com/watch?v=4ngoj6j4TXQ', 1) #очень мало комментов
        #generator = downloader.get_comments_from_url('https://www.youtube.com/watch?v=5honzRauhtE&list=RDSuQGfk9Gmgo&index=17', 1)  #много комменетов
        generator = downloader.get_comments_from_url('https://www.youtube.com/watch?v=MrTcmheQuAs&t=614s', 1) #~150комментов
        count = 0
        with io.open('comments.json', 'w', encoding='utf8') as fp:
            print('Downloaded %d comment(s)\r' % count)
            for comment in generator:
                count += 1
                print(count)
    except Exception as e:
        print(e)


main()





