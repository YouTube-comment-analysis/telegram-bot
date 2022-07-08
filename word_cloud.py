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


create_default_word_cloud("""
Что такое WordCloud?
Много раз вы могли видеть облако, заполненное множеством слов разного размера, которые представляют частоту или важность каждого слова. Это называется Облако тегов или WordCloud. В этом руководстве вы узнаете, как создать собственное WordCloud на Python и настроить его по своему усмотрению. Этот инструмент будет весьма удобен для изучения текстовых данных и оживления вашего отчета.

В этом уроке мы будем использовать набор данных обзора вин, взятый с веб- сайта Wine Enthusiast , чтобы узнать:

Как создать базовое облако слов из одного или нескольких текстовых документов
Отрегулируйте цвет, размер и количество текста внутри вашего облака слов
Замаскируйте свое облако слов в любую форму по вашему выбору
Маскируйте свое облако слов любым цветовым узором по вашему выбору
графика
Предпосылки
Вам нужно будет установить несколько пакетов ниже:

пустышка
панды
matplotlib
подушка
облако слов
Библиотека numpy— одна из самых популярных и полезных библиотек, которая используется для работы с многомерными массивами и матрицами. Он также используется в сочетании с Pandasбиблиотекой для анализа данных.

Модуль Python os— это встроенная библиотека, поэтому вам не нужно его устанавливать. Чтобы узнать больше об обработке файлов с помощью модуля os, вам будет полезен этот учебник по DataCamp .

Для визуализации matplotlibэто базовая библиотека, которая позволяет запускать и строить на ее основе множество других библиотек, в том числе seabornили wordcloudкоторые вы будете использовать в этом руководстве. Библиотека pillowпредставляет собой пакет, позволяющий читать изображения. Его учебник можно найти здесь . Pillow — это оболочка для PIL — Python Imaging Library. Эта библиотека понадобится вам для чтения изображения в качестве маски для облака слов.

wordcloudможет быть немного сложно установить. Если вам это нужно только для построения базового облака слов, тогда pip install wordcloudили conda install -c conda-forge wordcloudбудет достаточно. Однако последняя версия с возможностью маскировать облако в любую форму по вашему выбору требует другого метода установки, как показано ниже:

git clone https://github.com/amueller/word_cloud.git
cd word_cloud
pip install .
Набор данных:
В этом руководстве используется набор данных обзоров вин от Kaggle . Эта коллекция представляет собой отличный набор данных для обучения без пропущенных значений (для обработки которых потребуется время) и большого количества текста (обзоры вин), категорийных и числовых данных.

Теперь давайте начнем!
Прежде всего, вы загружаете все необходимые библиотеки:

# Start with loading all necessary libraries
import numpy as np
import pandas as pd
from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

import matplotlib.pyplot as plt
% matplotlib inline
c:\intelpython3\lib\site-packages\matplotlib\__init__.py:
import warnings
warnings.filterwarnings("ignore")
Если у вас более 10 библиотек, организуйте их по разделам (например, базовые библиотеки, визуализация, модели и т. д.), используя комментарии в коде, чтобы сделать ваш код чистым и простым для понимания.
Теперь, используя pandas read_csvдля загрузки фрейма данных. Обратите внимание на использование index_col=0значения, которое мы не читаем в имени строки (индексе) в качестве отдельного столбца.

# Load in the dataframe
df = pd.read_csv("data/winemag-data-130k-v2.csv", index_col=0)
# Looking at first 5 rows of the dataset
df.head()
набор данных
Вы можете распечатать некоторую основную информацию о наборе данных, используя в print()сочетании с .format(), чтобы получить красивую распечатку.

print("There are {} observations and {} features in this dataset. \n".format(df.shape[0],df.shape[1]))

print("There are {} types of wine in this dataset such as {}... \n".format(len(df.variety.unique()),
                                                                           ", ".join(df.variety.unique()[0:5])))

print("There are {} countries producing wine in this dataset such as {}... \n".format(len(df.country.unique()),
                                                                                      ", ".join(df.country.unique()[0:5])))
There are 129971 observations and 13 features in this dataset.

There are 708 types of wine in this dataset such as White Blend, Portuguese Red, Pinot Gris, Riesling, Pinot Noir...

There are 44 countries producing wine in this dataset such as Italy, Portugal, US, Spain, France...
df[["country", "description","points"]].head()
 	страна	описание	точки
0	Италия	Ароматы включают тропические фрукты, ракиту, серу...	87
1	Португалия	Это зрелое и фруктовое вино, мягкое...	87
2	НАС	Терпкий и острый, аромат мякоти лайма и...	87
3	НАС	Кожура ананаса, цедра лимона и цветки апельсина...	87
4	НАС	Как и обычный розлив 2012 года, этот...	87
Для сравнения групп объекта можно использовать groupby()и вычислять сводную статистику.

С набором винных данных вы можете сгруппировать по странам и посмотреть либо сводную статистику по баллам и цене всех стран, либо выбрать самые популярные и дорогие.

# Groupby by country
country = df.groupby("country")

# Summary statistic of all countries
country.describe().head()
набор данных
Это выбирает 5 лучших средних баллов среди всех 44 стран:

country.mean().sort_values(by="points",ascending=False).head()
 	точки	цена
страна	 	 
Англия	91.581081	51.681159
Индия	90.222222	13.333333
Австрия	90.101345	30.762772
Германия	89.851732	42.257547
Канада	89.369650	35.712598
Вы можете построить график количества вин по странам, используя метод графика Pandas DataFrame и Matplotlib. Если вы не знакомы с Matplotlib, предлагаю бегло ознакомиться с этим туториалом .

plt.figure(figsize=(15,10))
country.size().sort_values(ascending=False).plot.bar()
plt.xticks(rotation=50)
plt.xlabel("Country of Origin")
plt.ylabel("Number of Wines")
plt.show()
график
Среди 44 стран, производящих вино, США имеют более 50 000 видов вин в наборе данных обзора вин, что вдвое больше, чем следующая в рейтинге: Франция - страна, известная своим вином. Италия также производит много качественного вина, около 20 000 вин открыты для обзора.

Количество важнее качества?
Давайте теперь посмотрим на график всех 44 стран по вину с самым высоким рейтингом, используя ту же технику построения графика, что и выше:

plt.figure(figsize=(15,10))
country.max().sort_values(by="points",ascending=False)["points"].plot.bar()
plt.xticks(rotation=50)
plt.xlabel("Country of Origin")
plt.ylabel("Highest point of Wines")
plt.show()
график
Австралия, США, Португалия, Италия и Франция имеют 100-балльное вино. Если вы заметили, Португалия занимает 5-е место, а Австралия — 9-е место по количеству производимых вин в наборе данных, и в обеих странах менее 8000 видов вина.
Это небольшое исследование данных, чтобы познакомиться с набором данных, который вы используете сегодня. Теперь вы начнете погружаться в основное блюдо: WordCloud .

Настройка базового WordCloud
WordCloud — это метод, показывающий, какие слова наиболее часто встречаются в заданном тексте. Первое, что вы можете сделать, прежде чем использовать какие-либо функции, — это проверить строку документации функции и просмотреть все обязательные и необязательные аргументы. Для этого введите ?functionи запустите его, чтобы получить всю информацию.

?WordCloud
[1;31mInit signature:[0m [0mWordCloud[0m[1;33m([0m[0mfont_path[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mwidth[0m[1;33m=[0m[1;36m400[0m[1;33m,[0m [0mheight[0m[1;33m=[0m[1;36m200[0m[1;33m,[0m [0mmargin[0m[1;33m=[0m[1;36m2[0m[1;33m,[0m [0mranks_only[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mprefer_horizontal[0m[1;33m=[0m[1;36m0.9[0m[1;33m,[0m [0mmask[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mscale[0m[1;33m=[0m[1;36m1[0m[1;33m,[0m [0mcolor_func[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mmax_words[0m[1;33m=[0m[1;36m200[0m[1;33m,[0m [0mmin_font_size[0m[1;33m=[0m[1;36m4[0m[1;33m,[0m [0mstopwords[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mrandom_state[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mbackground_color[0m[1;33m=[0m[1;34m'black'[0m[1;33m,[0m [0mmax_font_size[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mfont_step[0m[1;33m=[0m[1;36m1[0m[1;33m,[0m [0mmode[0m[1;33m=[0m[1;34m'RGB'[0m[1;33m,[0m [0mrelative_scaling[0m[1;33m=[0m[1;36m0.5[0m[1;33m,[0m [0mregexp[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mcollocations[0m[1;33m=[0m[1;32mTrue[0m[1;33m,[0m [0mcolormap[0m[1;33m=[0m[1;32mNone[0m[1;33m,[0m [0mnormalize_plurals[0m[1;33m=[0m[1;32mTrue[0m[1;33m,[0m [0mcontour_width[0m[1;33m=[0m[1;36m0[0m[1;33m,[0m [0mcontour_color[0m[1;33m=[0m[1;34m'black'[0m[1;33m)[0m[1;33m[0m[0m
[1;31mDocstring:[0m     
Word cloud object for generating and drawing.

Parameters
----------
font_path : string
    Font path to the font that will be used (OTF or TTF).
    Defaults to DroidSansMono path on a Linux machine. If you are on
    another OS or don't have this font; you need to adjust this path.

width : int (default=400)
    Width of the canvas.

height : int (default=200)
    Height of the canvas.

prefer_horizontal : float (default=0.90)
    The ratio of times to try horizontal fitting as opposed to vertical.
    If prefer_horizontal < 1, the algorithm will try rotating the word
    if it doesn't fit. (There is currently no built-in way to get only
    vertical words.)

mask : nd-array or None (default=None)
    If not None, gives a binary mask on where to draw words. If mask is not
    None, width and height will be ignored, and the shape of mask will be
    used instead. All white (#FF or #FFFFFF) entries will be considered
    "masked out" while other entries will be free to draw on. [This
    changed in the most recent version!]

contour_width: float (default=0)
    If mask is not None and contour_width > 0, draw the mask contour.

contour_color: color value (default="black")
    Mask contour color.

scale : float (default=1)
    Scaling between computation and drawing. For large word-cloud images,
    using scale instead of larger canvas size is significantly faster, but
    might lead to a coarser fit for the words.

min_font_size : int (default=4)
    Smallest font size to use. Will stop when there is no more room in this
    size.

font_step : int (default=1)
    Step size for the font. font_step > 1 might speed up computation but
    give a worse fit.

max_words : number (default=200)
    The maximum number of words.

stopwords : set of strings or None
    The words that will be eliminated. If None, the build-in STOPWORDS
    list will be used.

background_color : color value (default="black")
    Background color for the word cloud image.

max_font_size : int or None (default=None)
    Maximum font size for the largest word. If None, the height of the image is
    used.

mode : string (default="RGB")
    Transparent background will be generated when mode is "RGBA" and
    background_color is None.

relative_scaling : float (default=.5)
    Importance of relative word frequencies for font-size.  With
    relative_scaling=0, only word-ranks are considered.  With
    relative_scaling=1, a word that is twice as frequent will have twice
    the size.  If you want to consider the word frequencies and not only
    their rank, relative_scaling around .5 often looks good.

    .. versionchanged: 2.0
        Default is now 0.5.

color_func : callable, default=None
    Callable with parameters word, font_size, position, orientation,
    font_path, random_state that returns a PIL color for each word.
    Overwrites "colormap".
    See colormap for specifying a matplotlib colormap instead.

regexp : string or None (optional)
    Regular expression to split the input text into tokens in process_text.
    If None is specified, ``r"\w[\w']+"`` is used.

collocations : bool, default=True
    Whether to include collocations (bigrams) of two words.

    .. versionadded: 2.0

colormap : string or matplotlib colormap, default="viridis"
    Matplotlib colormap to randomly draw colors from for each word.
    Ignored if "color_func" is specified.

    .. versionadded: 2.0

normalize_plurals : bool, default=True
    Whether to remove trailing 's' from words. If True and a word
    appears with and without a trailing 's', the one with trailing 's'
    is removed and its counts are added to the version without
    trailing 's' -- unless the word ends with 'ss'.

Attributes
----------
``words_`` : dict of string to float
    Word tokens with associated frequency.

    .. versionchanged: 2.0
        ``words_`` is now a dictionary

``layout_`` : list of tuples (string, int, (int, int), int, color))
    Encodes the fitted word cloud. Encodes for each word the string, font
    size, position, orientation, and color.

Notes
-----
Larger canvases will make the code significantly slower. If you need a
large word cloud, try a lower canvas size, and set the scale parameter.

The algorithm might give more weight to the ranking of the words
then their actual frequencies, depending on the ``max_font_size`` and the
scaling heuristic.
[1;31mFile:[0m           c:\intelpython3\lib\site-packages\wordcloud\wordcloud.py
[1;31mType:[0m           type
Вы можете видеть, что единственным обязательным аргументом для объекта WordCloud является текст , а все остальные необязательны.

Итак, давайте начнем с простого примера: использование описания первого наблюдения в качестве входных данных для облака слов. Три шага:

Извлечь обзор (текстовый документ)
Создать и сгенерировать изображение wordcloud
Отображение облака с помощью matplotlib
# Start with one review:
text = df.description[0]

# Create and generate a word cloud image:
wordcloud = WordCloud().generate(text)

# Display the generated image:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
облако слов
Большой! Вы можете видеть, что в первом обзоре много говорилось о сухих вкусах и ароматах вина.

Теперь измените некоторые необязательные аргументы WordCloud, такие как max_font_size, max_wordи background_color.

# lower max_font_size, change the maximum number of word and lighten the background:
wordcloud = WordCloud(max_font_size=50, max_words=100, background_color="white").generate(text)
plt.figure()
plt.imshow(wordcloud, interpolation="bilinear")
plt.axis("off")
plt.show()
облако слов
Ох, кажется, max_font_sizeздесь не может быть хорошей идеей. Это затрудняет понимание различий между частотами слов. Однако осветление фона облегчает чтение облака.

Если вы хотите сохранить изображение, WordCloud предоставляет функциюto_file

# Save the image in the img folder:
wordcloud.to_file("img/first_review.png")
<wordcloud.wordcloud.WordCloud at 0x16f1d704978>
Результат будет выглядеть так, когда вы загрузите их:

облако слов
Вы, наверное, заметили аргумент interpolation="bilinear"в файле plt.imshow(). Это делается для того, чтобы отображаемое изображение выглядело более плавно. Для получения дополнительной информации об этом выборе, вот полезная ссылка, чтобы узнать больше об этом выборе.

Итак, теперь вы объедините все обзоры вин в один большой текст и создадите большое жирное облако, чтобы увидеть, какие характеристики наиболее характерны для этих вин.

text = " ".join(review for review in df.description)
print ("There are {} words in the combination of all review.".format(len(text)))
There are 31661073 words in the combination of all review.
# Create stopword list:
stopwords = set(STOPWORDS)
stopwords.update(["drink", "now", "wine", "flavor", "flavors"])

# Generate a word cloud image
wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(text)

# Display the generated image:
# the matplotlib way:
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()
облако слов
Оооо, кажется, черная вишня и насыщенность — самые упоминаемые характеристики, а Каберне Совиньон — самая популярная из них. Это согласуется с тем фактом, что Каберне Совиньон «является одним из наиболее широко известных в мире сортов винограда для красных вин. Его выращивают почти во всех основных винодельческих странах в самых разных климатических условиях от канадской долины Оканаган до ливанской долины Бекаа». [1]

А теперь давайте нальем эти слова в чашу вина!
Серьезно,
даже бутылку вина, если хотите!

Чтобы создать форму для вашего облака слов, сначала вам нужно найти файл PNG, который станет маской. Ниже приведен хороший пример, который доступен в Интернете:

маска
Не все изображения масок имеют одинаковый формат, что приводит к разным результатам, поэтому функция WordCloud не работает должным образом. Чтобы убедиться, что ваша маска работает, давайте посмотрим на нее в форме массива numpy:

wine_mask = np.array(Image.open("img/wine_mask.png"))
wine_mask
array([[0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       ...,
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0],
       [0, 0, 0, ..., 0, 0, 0]], dtype=uint8)
Принцип работы функций маскирования заключается в том, что он требует, чтобы вся белая часть маски была 255, а не 0 (целочисленный тип). Это значение представляет «интенсивность» пикселя. Значения 255 соответствуют чисто белому цвету, а значения 1 — черному. Здесь вы можете использовать предоставленную ниже функцию для преобразования вашей маски, если ваша маска имеет тот же формат, что и выше. Обратите внимание, если у вас есть маска с фоном не 0, а 1 или 2, настройте функцию в соответствии с вашей маской.

Во-первых, вы используете transform_format()функцию, чтобы поменять местами число 0 на 255.

def transform_format(val):
    if val == 0:
        return 255
    else:
        return val
Затем создайте новую маску той же формы, что и маска, которая у вас есть, и примените функцию transform_format()к каждому значению в каждой строке предыдущей маски.

# Transform your mask into a new one that will work with the function:
transformed_wine_mask = np.ndarray((wine_mask.shape[0],wine_mask.shape[1]), np.int32)

for i in range(len(wine_mask)):
    transformed_wine_mask[i] = list(map(transform_format, wine_mask[i]))
Теперь у вас есть новая маска в правильной форме. Распечатайте преобразованную маску — лучший способ проверить, работает ли функция нормально.

# Check the expected result of your mask
transformed_wine_mask
array([[255, 255, 255, ..., 255, 255, 255],
       [255, 255, 255, ..., 255, 255, 255],
       [255, 255, 255, ..., 255, 255, 255],
       ...,
       [255, 255, 255, ..., 255, 255, 255],
       [255, 255, 255, ..., 255, 255, 255],
       [255, 255, 255, ..., 255, 255, 255]])
Хорошо! С правильной маской вы можете начать создавать облако слов с выбранной вами формой. Обратите внимание, что в WordCloudфункции есть maskаргумент, который принимает преобразованную маску, которую вы создали выше. И contour_width, contour_colorкак следует из их названия, являются аргументами для настройки характеристик контура облака. Винная бутылка, которая у вас здесь, — это бутылка красного вина, поэтому огнеупорный кирпич кажется хорошим выбором для цвета контура. Для большего выбора цвета вы можете взглянуть на эту таблицу цветовых кодов .

# Create a word cloud image
wc = WordCloud(background_color="white", max_words=1000, mask=transformed_wine_mask,
               stopwords=stopwords, contour_width=3, contour_color='firebrick')

# Generate a wordcloud
wc.generate(text)

# store to file
wc.to_file("img/wine.png")

# show
plt.figure(figsize=[20,10])
plt.imshow(wc, interpolation='bilinear')
plt.axis("off")
plt.show()
облако слов
Вуаля! Вы создали облако слов в форме винной бутылки! Похоже, что в описаниях вин чаще всего упоминается черешня, фруктовые вкусы и полнотелые характеристики вина. Теперь давайте подробнее рассмотрим обзоры для каждой страны и построим облако слов, используя флаг каждой страны. Чтобы вам было легко представить, это пример, который вы скоро создадите:

флаг сша
Создание Wordcloud по цветовому шаблону
Вы можете объединить все обзоры пяти стран, в которых больше всего вин. Чтобы найти эти страны, вы можете либо посмотреть график зависимости страны от количества вина выше, либо использовать группу, которую вы получили выше, чтобы найти количество наблюдений для каждой страны (каждой группы) и sort_values()с аргументом ascending=Falseдля сортировки по убыванию.

country.size().sort_values(ascending=False).head()
country
US          54504
France      22093
Italy       19540
Spain        6645
Portugal     5691
dtype: int64
Итак, теперь у вас есть 5 ведущих стран: США, Франция, Италия, Испания и Португалия. Вы можете изменить количество стран, указав выбранный вами номер внутри страны, head()как показано ниже .

""",
                          'test')

