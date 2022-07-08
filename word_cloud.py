import PIL.Image as Image
from wordcloud import WordCloud, wordcloud, ImageColorGenerator
import numpy as np
import matplotlib.pyplot as plt

stop_words = " ".join(open('word_cloud/stop-words.txt', 'r').readlines())
cloud_mask = np.array(Image.open("word_cloud/cloud.png"))


def create_default_word_cloud(text: str, file_name: str) -> str:
    word_cloud = WordCloud(max_words=80, background_color='white',
                           min_word_length=3, stopwords=stop_words,
                           mask=cloud_mask).generate(text)
    path = f'{file_name}.png'
    word_cloud.to_file(path)
    return path


def create_adoptive_background_word_cloud(text: str, png_mask_path: str, file_name: str) -> str:
    mask = np.array(Image.open(png_mask_path))
    word_cloud = WordCloud(max_words=80, background_color='white',
                           min_word_length=3, stopwords=stop_words,
                           mask=mask).generate(text)
    image_colors = ImageColorGenerator(mask)
    plt.imshow(word_cloud.recolor(color_func=image_colors), interpolation="bilinear")
    plt.axis("off")
    path = f'{file_name}.png'
    plt.savefig(path, format="png", bbox_inches='tight')
    return path

