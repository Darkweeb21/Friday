import json
import threading
import tkinter as tk
from Backend.Model import FirstlayerDMM
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.Automation import Automation
from Backend.SpeechToText import speech_recognition, set_assistant_status
from Backend.TextToSpeech import text_to_speech
from Backend.Chatbox import chatbot
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import os
import subprocess
import logging

from Frontend.GUI import (
    query_modifier,
    set_assistant_status,
    answerModifier,
    get_assistant_status,
    get_temp_path,
    set_microphone_status,
    get_microphone_status,
    show_text_to_screen,
    GraphicalUserInterface,
    TEMP_DIR_PATH
)

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='assistant_debug.log')

# Global variables
env_vars = dotenv_values(".env")
username = env_vars["Username"]
assistant_name = env_vars["Assistantname"]
Default_message = f'''{username}:Hello{assistant_name}, How are you?
{assistant_name}:Welcome {username}. I am doing well. How may i help you'''
subprocesses = []
functions = ["open", "close", "play", "system", "content", "google search", 'youtube search']


def safe_show_text(text):
    """Safely show text to screen with error handling"""
    try:
        return show_text_to_screen(text, get_temp_path('Responses.data'))
    except Exception as e:
        logging.error(f"Error showing text: {e}")
        try:
            with open(get_temp_path('Responses.data'), 'w', encoding='utf-8') as f:
                f.write(text)
            return True
        except Exception as e:
            logging.error(f"Fallback error: {e}")
            return False


def ShowDefaultChatsIfNoChats():
    try:
        os.makedirs('Data', exist_ok=True)
        chat_log_path = os.path.join('Data', 'ChatLog.json')

        try:
            with open(chat_log_path, 'r', encoding='utf-8') as file:
                if len(file.read()) < 5:
                    with open(get_temp_path('Database.data'), 'w', encoding='utf-8') as db_file:
                        db_file.write(" ")
                    with open(get_temp_path('Responses.data'), 'w', encoding='utf-8') as resp_file:
                        resp_file.write(Default_message)
        except FileNotFoundError:
            with open(chat_log_path, 'w', encoding='utf-8') as file:
                file.write('[]')
            ShowDefaultChatsIfNoChats()
    except Exception as e:
        logging.error(f"Error in ShowDefaultChatsIfNoChats: {e}")


def ReadchatLogJson():
    try:
        with open(os.path.join('Data', 'ChatLog.json'), 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def ChatlogIntegration():
    json_data = ReadchatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"{username}: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"{assistant_name}: {entry['content']}\n"

    with open(get_temp_path('Database.data'), 'w', encoding='utf-8') as file:
        file.write(answerModifier(formatted_chatlog))


def ShowChatOnGUI():
    try:
        with open(get_temp_path('Database.data'), 'r', encoding='utf-8') as file:
            data = file.read()
            if data.strip():
                with open(get_temp_path('Responses.data'), 'w', encoding='utf-8') as resp_file:
                    resp_file.write(data)
    except Exception as e:
        logging.error(f"Error in ShowChatOnGUI: {e}")


def MainExecution():
    try:
        TaskExecution = False
        ImageExecution = False
        ImageGenerationQuery = ""

        set_assistant_status("Listening...")
        logging.debug("Starting speech recognition")

        query = speech_recognition()
        logging.debug(f"Speech recognition result: {query}")

        if not query:
            logging.warning("No speech detected")
            return False

        safe_show_text(f"{username}: {query}")
        set_assistant_status("Thinking.....")

        try:
            Decision = FirstlayerDMM(query)
            logging.debug(f"Decision from model: {Decision}")
        except Exception as e:
            logging.error(f"FirstlayerDMM error: {e}")
            return False

        G = any(i.startswith("genral") for i in Decision)
        R = any(i.startswith("realtime") for i in Decision)

        Merged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if i.startswith("genral") or i.startswith("realtime")]
        )

        for queries in Decision:
            if "generate" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True
                break

        if not TaskExecution:
            for queries in Decision:
                if any(queries.startswith(func) for func in functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True
                    break

        if ImageExecution:
            image_gen_path = os.path.join('Frontend', 'Files', 'ImageGeneration.data')
            with open(image_gen_path, 'w', encoding='utf-8') as file:
                file.write(f"{ImageGenerationQuery} ,True")
            try:
                p1 = subprocess.Popen(
                    ["python", os.path.join('Backend', 'ImageGenration.py')],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    shell=False
                )
                subprocesses.append(p1)
            except Exception as e:
                logging.error(f"ImageGenration.py error: {e}")

        if G and R or R:
            set_assistant_status("Searching...")
            try:
                answer = realtime_search_engine(query_modifier(Merged_query))
                safe_show_text(f"{assistant_name}: {answer}")
                set_assistant_status("Answering.....")
                text_to_speech(answer)
                return True
            except Exception as e:
                logging.error(f"Realtime search error: {e}")
                return False

        for queries in Decision:
            try:
                if "genral" in queries:
                    set_assistant_status("Thinking....")
                    query_final = queries.replace("genral", " ")
                    answer = chatbot(query_modifier(query_final))
                    safe_show_text(f"{assistant_name}: {answer}")
                    text_to_speech(answer)
                    return True
                elif "realtime" in queries:
                    set_assistant_status("Searching...")
                    query_final = queries.replace("realtime", " ")
                    answer = realtime_search_engine(query_modifier(query_final))
                    safe_show_text(f"{assistant_name}: {answer}")
                    set_assistant_status("Answering.....")
                    text_to_speech(answer)
                    return True
                elif "exit" in queries:
                    query_final = "Okay, Bye!"
                    answer = chatbot(query_modifier(query_final))
                    safe_show_text(f"{assistant_name}: {answer}")
                    set_assistant_status("Answering.....")
                    text_to_speech(answer)
                    for process in subprocesses:
                        process.terminate()
                    os._exit(0)
            except Exception as e:
                logging.error(f"Query processing error: {e}")
                continue

        return False
    except Exception as e:
        logging.error(f"MainExecution error: {e}")
        return False


def background_thread():
    while True:
        try:
            current_status = get_microphone_status()
            if current_status == "true":
                MainExecution()
            else:
                set_assistant_status("Available.....")
                sleep(0.1)
        except Exception as e:
            logging.error(f"Background thread error: {e}")
            sleep(1)


def InitialExecution():
    try:
        # Create necessary directories
        os.makedirs(os.path.join('Frontend', 'Files'), exist_ok=True)

        set_microphone_status("False")
        set_assistant_status("Initializing...")
        safe_show_text(' ')
        ShowDefaultChatsIfNoChats()
        ChatlogIntegration()
        ShowChatOnGUI()
        set_assistant_status("Ready...")
        logging.debug("InitialExecution completed successfully")
    except Exception as e:
        logging.error(f"InitialExecution error: {e}")


if __name__ == '__main__':
    try:
        # Initialize everything first
        InitialExecution()

        # Start the background thread
        background_thread = threading.Thread(target=background_thread, daemon=True)
        background_thread.start()

        # Create and run the GUI in the main thread
        root = tk.Tk()
        app = GraphicalUserInterface()
        root.mainloop()
    except Exception as e:
        logging.error(f"Main execution error: {e}")
        for process in subprocesses:
            try:
                process.terminate()
            except:
                pass