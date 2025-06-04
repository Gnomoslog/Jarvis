import os
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import random

# Инициализация синтезатора речи с грубоватым голосом
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Настройка грубоватого голоса
for voice in voices:
    if 'ru' in voice.id.lower() and 'male' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        break
else:
    engine.setProperty('voice', voices[0].id)

def speak(text):
    print(f"JARVIS: {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Слушаю...")
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            print("Распознаю...")
            query = r.recognize_google(audio, language='ru-RU').lower()
            print(f"Пользователь: {query}")
            return query
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Ошибка: {e}")
            return ""

def ask_ai(prompt):
    prompt_lower = prompt.lower()
    
    if any(w in prompt_lower for w in ['привет', 'здравствуй']):
        return random.choice(["Здравия желаю.", "Приветствую.", "Доброго времени суток."])
    
    elif any(w in prompt_lower for w in ['как дела', 'как работа']):
        return random.choice(["В норме.", "Исправно функционирую.", "Работаю."])
    
    elif any(w in prompt_lower for w in ['время', 'час']):
        return f"Сейчас {datetime.datetime.now().strftime('%H:%M')}"
    
    elif any(w in prompt_lower for w in ['дата', 'число', 'день', 'месяц']):
        return f"Сегодня {datetime.datetime.now().strftime('%d %B %Y')}"
    
    return random.choice(["Не понял.", "Уточните.", "Повторите."])

def greet():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        speak("Доброе утро.")
    elif 12 <= hour < 18:
        speak("Добрый день.")
    else:
        speak("Добрый вечер.")
    
    speak(f"Сегодня {datetime.datetime.now().strftime('%d %B %Y')}.")
    speak("Система готова.")

def handle_command(query):
    if not query:
        return True, None
    
    commands = {
        'открой браузер': ("Открываю.", lambda: webbrowser.open("https://google.com")),
        'время': (f"Время: {datetime.datetime.now().strftime('%H:%M')}", None),
        'дата': (f"Дата: {datetime.datetime.now().strftime('%d %B %Y')}", None),
        'спасибо': (random.choice(["Не за что.", "Без проблем."]), None),
        'выключись': ("Отключаюсь.", False)
    }
    
    for cmd, (response, action) in commands.items():
        if cmd in query:
            if action is False:
                return False, None
            if action:
                action()
            return True, response
    
    return True, None

def main():
    greet()
    while True:
        query = take_command()
        
        should_continue, response = handle_command(query)
        
        if not should_continue:
            break
            
        if response:
            speak(response)
        elif query:
            ai_response = ask_ai(query)
            speak(ai_response)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        speak("Прервано")
    except Exception as e:
        print(f"Ошибка: {e}")
        speak("Сбой системы")