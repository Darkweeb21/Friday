# Friday

# Friday AI Assistant

## Description
Friday is a versatile AI-powered personal assistant designed to simplify daily tasks through an intuitive GUI interface. It can open and close applications, perform web and real-time searches, generate images, and much more.

## Features
- **Open/Close Applications:** Launch or close apps effortlessly.
- **Web Search:** Search the web for information quickly.
- **Real-Time Search:** Get up-to-date information in real-time.
- **Image Generation:** Generate images based on text prompts.
- **GUI Interface:** User-friendly graphical interface for easy interaction.

## Installation
### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/friday-ai.git
   cd friday-ai
   ```
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root directory:
   ```bash
   touch .env
   ```
4. Add the following variables to the `.env` file:
   ```env
   CohereAPIkey= your api key
   Username= your username
   Assistantname= your ai name
   GROQ_API_KEY= your api key
   InputLangauge=en
   Assistantvoice=en-AU-NatashaNeural
   HuggingFaceAPIKey= your api key
   APP_DIRECTORY_PATH=
   DATA_DIRECTORY_PATH=
   ```
   > **Note:** Replace the placeholder values with your actual API keys and correct directory paths.

## Usage
1. Run the assistant:
   ```bash
   python main.py
   ```
2. Interact with the GUI to use features like app control, web search, and image generation.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.

---

**Developed with passion and innovation.**

