import requests
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import tempfile
import os
import heapq
import re

# Upewnij się, że pobrane są niezbędne zasoby NLTK
nltk.download('punkt')
nltk.download('stopwords')

# Funkcja do pobierania i zapisywania treści strony
def provide_link(url, file_prefix='temp_file_'):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all('p')
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, prefix=file_prefix, suffix='.txt') as tmp_file:
            tmp_file_name = tmp_file.name
            for p in paragraphs:
                paragraph_text = p.getText()
                sentences = sent_tokenize(paragraph_text)
                for sentence in sentences:
                    tmp_file.write(sentence + '\n')
        return tmp_file_name
    else:
        print(f'Błąd podczas pobierania strony: kod statusu {response.status_code}')
        return None

# Funkcja do generowania streszczenia
def generate_summary(file_path, compression_ratio=0.25):
    with open(file_path, "r") as file:
        text = file.read()
    sentences = sent_tokenize(text)
    word_frequencies = {}
    stop_words = set(stopwords.words("english"))

    for word in word_tokenize(text):
        if word.lower() not in stop_words:
            if word not in word_frequencies.keys():
                word_frequencies[word] = 1
            else:
                word_frequencies[word] += 1

    maximum_frequncy = max(word_frequencies.values())

    for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

    sentence_scores = {}
    for sent in sentences:
        for word in nltk.word_tokenize(sent.lower()):
            if word in word_frequencies.keys():
                if len(sent.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequencies[word]
                    else:
                        sentence_scores[sent] += word_frequencies[word]

    summary_sentences = heapq.nlargest(int(len(sentences) * compression_ratio), sentence_scores, key=sentence_scores.get)
    summary = ' '.join(summary_sentences)
    summary_file_path = file_path.replace('.txt', '_summary.txt')
    with open(summary_file_path, "w") as summary_file:
        summary_file.write(summary)
    return summary_file_path


