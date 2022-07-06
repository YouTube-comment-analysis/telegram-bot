class Comment:
    def __int__(self, video_url, text, date, is_reply, votes):
        self.video_url = video_url
        self.text = text
        self.date = date
        self.is_reply = is_reply
        self.votes = votes