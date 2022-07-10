import PIL.Image as Image
from wordcloud import WordCloud, wordcloud, ImageColorGenerator
import numpy as np
import matplotlib.pyplot as plt

import analysis
import database
from comment_scrapping.comment import Comment

"""
Примеры использования:
create_default_word_cloud('MrTcmheQuAs&t=614s', 'test')
create_adoptive_background_word_cloud('MrTcmheQuAs&t=614s', 'word_cloud/cloud.png', 'test-color')
"""


stop_words = list(map(lambda x: x[:-1], (open('word_cloud/stop-words.txt', 'r', encoding='UTF-8').readlines())))
cloud_mask = np.array(Image.open("word_cloud/cloud.png"))
save_path = ''


def get_all_normal_words(comments: str):
    comments_text = " ".join(list(map(lambda x: x.text, comments)))
    words = analysis.get_normal_phrases(comments_text.split('\n'))
    text = []
    for mess in words:
        for word in mess:
            text.append(word)
    all_words = " ".join(list(text))
    return all_words


def create_default_word_cloud(comments: [Comment], file_name: str) -> str:
    """Создать обычное облако слов, возвращает путь к файлу"""
    text = get_all_normal_words(comments)
    word_cloud = WordCloud(max_words=80, background_color='white',
                           min_word_length=3,
                           stopwords=stop_words,
                           mask=cloud_mask).generate(text)
    path = f'{save_path}{file_name}.png'
    word_cloud.to_file(path)
    return path


def create_adoptive_background_word_cloud(comments: [Comment], png_mask_path: str, file_name: str) -> str:
    """Создание облака слов по фото с копированием цвета фона под словом"""
    text = get_all_normal_words(comments)
    mask = np.array(Image.open(png_mask_path))
    word_cloud = WordCloud(max_words=80, background_color='white',
                           min_word_length=3, stopwords=stop_words,
                           mask=mask).generate(text)
    image_colors = ImageColorGenerator(mask)
    plt.imshow(word_cloud.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    path = f'{save_path}{file_name}.png'
    plt.savefig(path, format="png", bbox_inches='tight')
    return path



