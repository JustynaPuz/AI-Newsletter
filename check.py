import os

# Załóżmy, że te importy działają i są wcześniej zdefiniowane
from llama_cpp import Llama
from summarizer import provide_link, generate_summary

# Załadowanie modelu LLaMA
llm = Llama(model_path="llama-2-7b-chat.Q6_K.gguf")

# Pobranie linku do artykułu od użytkownika
article_link = input("Provide me with the link to the article: ")
tmp_file_name = provide_link(article_link)
summary_file_path = generate_summary(tmp_file_name)

if summary_file_path:
    with open(summary_file_path, 'r') as file:
        pure_text = file.read()

    user_question = input("Tell me what to do with provided article: ")

    # Dodanie "Q: " na początku, jeśli użytkownik nie dodał
    if not user_question.startswith("Q: "):
        user_question = "Q: " + user_question

    # Przygotowanie pełnego pytania z treścią artykułu
    full_question = f"{pure_text}\n\n{user_question} A: "

    # Wywołanie modelu z pytaniem użytkownika
    output = llm(
        full_question,
        stop=["Q:", "\n"],
        echo=True
    )

    # Wyświetlenie odpowiedzi
    print("A: " + output)

    # Usunięcie pliku tymczasowego
    os.remove(summary_file_path)
else:
    print("Failed to retrieve the article.")
