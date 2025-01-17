from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import dotenv_values
import os
import mtranslate as mt

# Get environment variables with default value
env_vars = dotenv_values(".env")
input_language = env_vars.get("InputLanguage", "en")  # Fixed spelling and added default

# Define HTML code for speech recognition
html_code = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new webkitSpeechRecognition() || new SpeechRecognition();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript;
            };

            recognition.onend = function() {
                recognition.start();
            };
            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.innerHTML = "";
        }
    </script>
</body>
</html>'''

# Replace the lang setting in HTML code
html_code = html_code.replace("recognition.lang = '';", f"recognition.lang = '{input_language}';")

# Use os.path.join for consistent path handling
current_dir = os.getcwd()
data_dir = os.path.join(current_dir, "Data")
voice_html_path = os.path.join("Data", "Voice.html")
temp_dir_path = os.path.join("Frontend", "Files")

# Ensure directories exist
os.makedirs(data_dir, exist_ok=True)
os.makedirs(temp_dir_path, exist_ok=True)

# Write HTML file
with open(voice_html_path, "w", encoding="utf-8") as f:
    f.write(html_code)

# Set up Chrome options
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize Chrome webdriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def set_assistant_status(status):
    status_file = os.path.join(temp_dir_path, "Status.data")
    with open(status_file, 'w', encoding="utf-8") as file:
        file.write(status)

def query_modifier(query):
    new_query = query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "where", "when", "which", "why", "whose", "whom",
                     "can you", "what's", "where's", "how's"]

    # Check if query is a question
    if any(word in new_query for word in question_words):
        if query_words[-1][-1] in [".", "?", "!"]:
            new_query = new_query[:-1] + "?"
        else:
            new_query = new_query + "?"
    else:
        if query_words[-1][-1] in [",", "?", "!"]:
            new_query = new_query[:-1] + "."
        else:
            new_query = new_query + "."
    return new_query.capitalize()

def universal_translator(text):
    english_translation = mt.translate(text, "en", "auto")
    return english_translation.capitalize()

def speech_recognition():
    file_url = f"file:///{voice_html_path}"
    driver.get(file_url)
    driver.find_element(by=By.ID, value="start").click()

    while True:
        try:
            text = driver.find_element(by=By.ID, value="output").text
            if text:
                driver.find_element(by=By.ID, value="end").click()

                if input_language.lower() == "en" or "en" in input_language.lower():
                    return query_modifier(text)
                else:
                    set_assistant_status("Translating......")
                    return query_modifier(universal_translator(text))
        except Exception as e:
            pass

if __name__ == "__main__":
    try:
        while True:
            text = speech_recognition()
            print(text)
    except KeyboardInterrupt:
        driver.quit()
