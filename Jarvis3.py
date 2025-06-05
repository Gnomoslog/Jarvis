import os
import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import random
import pyautogui
import subprocess
import time
import sys
import wolframalpha
import pyjokes
import wikipedia
from pathlib import Path

# Инициализация WolframAlpha
wolfram_client = wolframalpha.Client('9QH36Y-E39WXQJR2T')

# Проверка наличия pyautogui
try:
    import pyautogui
    PYAUIGUI_AVAILABLE = True
except ImportError:
    PYAUIGUI_AVAILABLE = False
    print("Предупреждение: pyautogui не установлен. Некоторые функции будут недоступны.")

# Инициализация синтезатора речи
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Настройка голоса
for voice in voices:
    if 'david' in voice.name.lower():
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 180)
        engine.setProperty('volume', 0.9)
        break
else:
    for voice in voices:
        if 'male' in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

def speak(text):
    """Произносит текст и выводит его в консоль"""
    print(f"JARVIS: {text}")
    try:
        engine.say(text)
        engine.runAndWait()
        time.sleep(0.2)
    except Exception as e:
        print(f"Ошибка синтеза речи: {e}")

def take_command():
    """Получает голосовую команду от пользователя"""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            r.adjust_for_ambient_noise(source, duration=1)
            print("Слушаю...")
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            print("Анализирую...")
            query = r.recognize_google(audio, language='ru-RU').lower()
            print(f"Вы: {query}")
            return query
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print(f"Ошибка сервиса распознавания: {e}")
            return ""
        except Exception as e:
            print(f"Ошибка: {e}")
            return ""

def close_google_tab():
    """Закрывает текущую вкладку браузера"""
    if not PYAUIGUI_AVAILABLE:
        return "Функция закрытия вкладки недоступна"
    try:
        pyautogui.hotkey('ctrl', 'w')
        return "Вкладка закрыта"
    except Exception as e:
        return f"Ошибка: {str(e)}"

def system_shutdown():
    """Возвращает команды для управления системой"""
    return {
        'выключить компьютер': 'shutdown /s /t 0',
        'перезагрузить компьютер': 'shutdown /r /t 0',
        'режим сна': 'rundll32.exe powrprof.dll,SetSuspendState 0,1,0'
    }


    
def tell_joke():
    """Рассказывает случайный анекдот"""
    try:
        joke = pyjokes.get_joke(language='ru')
        return joke
    except:
        return "Почему программисты путают Хэллоуин и Рождество? Потому что 31 OCT = 25 DEC"

def calculate(expression):
    """Выполняет математические вычисления"""
    try:
        # Безопасное вычисление
        allowed_chars = set('0123456789+-*/.() ')
        if not all(c in allowed_chars for c in expression):
            return "Недопустимые символы в выражении"
        result = eval(expression, {'__builtins__': None}, {})
        return f"Результат: {result}"
    except:
        return "Не могу вычислить это выражение"

def search_wikipedia(query):
    """Ищет информацию в Википедии"""
    try:
        wikipedia.set_lang("ru")
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Уточните запрос. Возможные варианты: {', '.join(e.options[:3])}"
    except wikipedia.exceptions.PageError:
        return "Статья не найдена"
    except:
        return "Не удалось получить информацию"

def smart_response(query):
    """Использует WolframAlpha для ответов на вопросы"""
    try:
        res = wolfram_client.query(query)
        answer = next(res.results).text
        return answer
    except StopIteration:
        return "Ответ не найден"
    except:
        responses = [
            "Не удалось найти ответ",
            "Попробуйте переформулировать вопрос",
            "Информация не найдена"
        ]
        return random.choice(responses)

def handle_command(query):
    """Обрабатывает команды пользователя"""
    if not query:
        return True, None
    
    # Команды выключения системы
    shutdown_cmds = system_shutdown()
    for cmd in shutdown_cmds:
        if cmd in query:
            try:
                os.system(shutdown_cmds[cmd])
                return False, "Выполняю команду"
            except Exception as e:
                return True, f"Ошибка выполнения: {str(e)}"

    # Основные команды
    commands = {
        'открой браузер': ("Открываю браузер", lambda: webbrowser.open("https://google.com")),
        'включи youtube': ("Открываю YouTube", lambda: webbrowser.open("https://youtube.com")),
        'время': (f"Сейчас {datetime.datetime.now().strftime('%H:%M')}", None),
        'дата': (f"Сегодня {datetime.datetime.now().strftime('%d %B %Y')}", None),
        'спасибо': ("Всегда пожалуйста", None),
        'выключись': ("До свидания", False),
        'выкл': ("До свидания", False),
        'закрой вкладку': (close_google_tab(), None),
        'закрой браузер': ("Закрываю браузер", lambda: os.system("taskkill /f /im chrome.exe")),
        'расскажи анекдот': (tell_joke(), None),
        'найди в википедии': (search_wikipedia(query.replace('найди в википедии', '').strip()), None),
        'посчитай': (calculate(query.replace('посчитай', '').strip()), None),
    }
    
    # Команды открытия приложений
    if 'открой' in query:
        app_name = query.replace('открой', '').strip()
        return True, open_application(app_name)
    
    # Интеллектуальные запросы
    if 'найди' in query or 'что такое' in query:
        return True, smart_response(query)
    
    # Поиск совпадений с командами
    for cmd, (response, action) in commands.items():
        if cmd in query:
            if action is False:
                return False, None
            if action:
                try:
                    action()
                except Exception as e:
                    return True, f"Ошибка выполнения: {str(e)}"
            return True, response
    
    return True, None

def main():
    """Основной цикл программы"""
    try:
        speak("Система активирована")
        
        # Приветствие в зависимости от времени суток
        hour = datetime.datetime.now().hour
        if 0 <= hour < 6:
            speak("Доброй ночи")
        elif 6 <= hour < 12:
            speak("Доброе утро")
        elif 12 <= hour < 18:
            speak("Добрый день")
        else:
            speak("Добрый вечер")
        
        speak(f"Сегодня {datetime.datetime.now().strftime('%d %B %Y')}")
        
        # Основной цикл обработки команд
        while True:
            query = take_command()
            should_continue, response = handle_command(query)
            
            if not should_continue:
                break
                
            if response:
                speak(response)
            elif query:
                response = smart_response(query)
                speak(response)
                
    except KeyboardInterrupt:
        speak("Сессия завершена")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
        speak("Произошла системная ошибка")
    finally:
        # Завершение работы
        sys.exit(0)

if __name__ == "__main__":
    main()