from llama_cpp import Llama

# Tworzenie Llamy bożej z użyciem modelu
llm = Llama(
    model_path="llama-2-7b-chat.Q6_K.gguf"
)

# Pobieranie pytania od użytkownika w wersji terminalowej
user_question = input("Ask me a question: ")

# Dodanie "Q: " na początku, jeśli użytkownik nie dodał
if not user_question.startswith("Q: "):
    user_question = "Q: " + user_question

# Wywołanie modelu z pytaniem użytkownika
output = llm(
    user_question + " Answer: ",
    max_tokens=200,
    stop=["Q:", "\n"],
    echo=True
)
# print(output) - wyswietlanie z metadanymi
# Wyświetlenie odpowiedzi (wyrzuciłem te metadane bo mnie wkurwiały)
answer_text = output['choices'][0]['text']
# print(answer_text) - wyswietlanie bez metadanych
answer_part = answer_text.split("A: ")[-1]  # Dzieli tekst na części względem " A: " i bierze ostatnią część
print("A: " + answer_part)