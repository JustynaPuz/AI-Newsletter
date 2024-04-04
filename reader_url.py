import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize
import tempfile
import os
from gensim.summarization import summarize


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
def generate_summary(file_path, compression_ratio=0.4):
    with open(file_path, "r") as file:
        text = file.read()
    summary = summarize(text, ratio=compression_ratio)
    summary_file_path = file_path.replace('.txt', '_summary.txt')
    with open(summary_file_path, "w") as summary_file:
        summary_file.write(summary)
    return summary_file_path


# Główna część skryptu
if __name__ == "__main__":
    # Pobieranie i przetwarzanie treści strony
    url = "https://example.com"
    temp_file_path = provide_link(url)
    if temp_file_path:
        print(f"Treść strony zapisana w: {temp_file_path}")
        # Generowanie i zapisywanie streszczenia
        summary_file_path = generate_summary(temp_file_path)
        print(f"Streszczenie zapisane w: {summary_file_path}")
        # Opcjonalnie: usunięcie oryginalnego pliku
        os.remove(temp_file_path)
