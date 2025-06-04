import os
import openai
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import random
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Инициализация синтезатора речи
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Попытка найти русский голос
for voice in voices:
    if 'russian' in voice.languages or 'ru' in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break
else:
    engine.setProperty('voice', voices[1].id)  # Fallback на первый доступный голос

engine.setProperty('rate', 180)  # Скорость речи

# Функция для озвучивания текста
def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

# Функция для распознавания речи
def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)  # Настройка для шумоподавления
        print("Слушаю...")
        audio = r.listen(source, phrase_time_limit=5)  # Ограничение времени записи
    
    try:
        print("Распознаю...")
        query = r.recognize_google(audio, language='ru-RU').lower()
        print(f"Пользователь: {query}\n")
        return query
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return ""
    except Exception as e:
        print(f"Ошибка распознавания: {e}")
        return ""

# Функция для обработки команд с помощью ИИ
def ask_ai(prompt):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты Джарвис из фильма 'Железный человек'. Отвечай на русском языке кратко и вежливо. Используй обращение 'сэр'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7  # Для более креативных ответов
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"

# Приветствие
def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Доброе утро, сэр.")
    elif 12 <= hour < 18:
        speak("Добрый день, сэр.")
    else:
        speak("Добрый вечер, сэр.")
    speak("Я Джарвис. Чем могу помочь?")

# Основные команды
def handle_command(query):
    if not query:
        return True
    
    # Локальные команды
    if any(word in query for word in ['открой браузер', 'запусти браузер']):
        speak("Открываю браузер, сэр.")
        webbrowser.open("https://www.google.com")
        return True
        
    elif any(word in query for word in ['который час', 'сколько времени', 'текущее время']):
        str_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"Сейчас {str_time}, сэр.")
        return True
        
    elif 'спасибо' in query:
        responses = ["Всегда к вашим услугам, сэр.", "Не стоит благодарности.", "Для вас - всё."]
        speak(random.choice(responses))
        return True
        
    elif any(word in query for word in ['пока', 'выключись', 'заверши работу']):
        speak("До свидания, сэр. Всегда к вашим услугам.")
        return False
    
    return False

# Основная функция
def main():
    greet()
    while True:
        query = take_command()
        
        if not handle_command(query):
            break
            
        if query:  # Если команда не была обработана локально
            ai_response = ask_ai(query)
            speak(ai_response)

if __name__ == "__main__":
    main()