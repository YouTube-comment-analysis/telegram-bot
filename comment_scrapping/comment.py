class Comment:
    def __init__(self, id: str, video_url=None, text=None, date=None, is_reply=None, votes=None):
        self.id = id
        self.video_url = video_url
        self.text = text
        self.date = date
        self.is_reply = is_reply
        self.votes = votes
