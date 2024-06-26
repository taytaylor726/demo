import jieba
import requests
import streamlit as st
from streamlit_echarts import st_echarts
from collections import Counter
from PIL import Image
from wordcloud import WordCloud
import re
import string
import pandas as pd  # 导入pandas库


# 定义数据清洗函数
def clean_text(text):
    text = text.replace('\n', '')
    text = text.replace(' ', '')
    text = text.strip()
    return text

# 定义分词函数
def segment(text):
    stopwords = ['的', '了', '在', '是', '我', '你', '他', '她', '它', '们', '这', '那', '之', '与', '和', '或', '虽然', '但是', '然而', '因此']
    # 移除标点符号和换行符
    punctuation = "、，。！？；：“”‘’~@#￥%……&*（）【】｛｝+-*/=《》<>「」『』【】〔〕｟｠«»“”‘’'':;,/\\|[]{}()$^"
    text = text.translate(str.maketrans("", "", punctuation)).replace('\n', '')
    words = jieba.lcut(text)
    words = [word for word in words if word not in stopwords]
    return words

# Removing punctuation, numbers
def remove_punctuation(text):
    punctuation = string.punctuation
    text = text.translate(str.maketrans('', '', punctuation))
    return re.sub('\d+', '', text)


def stem_words(words):
    # Stemming words
    from nltk.stem import PorterStemmer
    stemmer = PorterStemmer()
    stemmed = []
    for word in words:
        stemmed.append(stemmer.stem(word))
    return stemmed


def remove_stopwords(words):
    # Filtering stopwords
    from nltk.corpus import stopwords
    stopwords = set(stopwords.words('english'))
    return [word for word in words if word not in stopwords]


# removing html tags

def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def extract_body_text(html):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find('body').get_text()
    return text


def read_txtfile():
    # streamlit 读取txt文件示例
    st.write('streamlit 读取txt文件示例')
    from pathlib import Path

    filePath = Path(__file__).parent / "stop_words.txt"

    if filePath.is_file():
        with open(filePath, 'r') as f:
            data = f.read()
            st.write(data)
    else:
        st.write("File not found")

def generate_wordcloud(text):
    # 使用WordCloud生成词云
    wordcloud = WordCloud(font_path='simhei.ttf', background_color='white', width=800, height=400, margin=2).generate(
        text)
    # 将词云保存为图片
    image = wordcloud.to_image()
    return image

def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# Welcome to Streamlit! 👋")

    url = st.text_input('请输入网页url:')

    if url:
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        text = extract_body_text(text)

        text = remove_html_tags(text)
        text = remove_punctuation(text)

        text = clean_text(text)
        words = segment(text)
        word_counts = Counter(words)

        # 创建一个DataFrame来存储词频统计结果
        df = pd.DataFrame(word_counts.most_common(20), columns=['Word', 'Count'])

        # 使用streamlit展示表格
        st.table(df)

        word_string = ' '.join(words)  # 将分词后的列表转换为字符串，供词云使用

        # 生成词云图像并展示
        wordcloud_image = generate_wordcloud(word_string)
        st.image(wordcloud_image, caption='词频统计词云', use_column_width=True)

        # 使用ECharts展示词频柱状图
        top_words = word_counts.most_common(20)

        wordcloud_options = {
            "tooltip": {
                "trigger": 'item',
                "formatter": '{b} : {c}'
            },
            "xAxis": [{
                "type": "category",
                "data": [word for word, count in top_words],
                "axisLabel": {
                    "interval": 0,
                    "rotate": 30
                }
            }],
            "yAxis": [{"type": "value"}],
            "series": [{
                "type": "bar",
                "data": [count for word, count in top_words]
            }]
        }

        st_echarts(wordcloud_options, height='500px')


if __name__ == "__main__":
    run()