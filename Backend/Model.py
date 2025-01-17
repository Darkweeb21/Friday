import cohere
from rich import print
from dotenv import load_dotenv
import os
import sys


def initialize_cohere_client():
    """Initialize the Cohere client with proper error handling."""
    load_dotenv()

    cohere_api_key = (
            os.getenv("CohereAPIkey") or
            os.getenv("COHERE_API_KEY") or
            os.getenv("CO_API_KEY")
    )

    if not cohere_api_key:
        print("[red]Error: Cohere API key not found![/red]")
        print("""
Please ensure you have set up your API key using one of these methods:
1. Create a .env file with: CohereAPIkey=your_api_key_here
2. Set an environment variable: COHERE_API_KEY=your_api_key_here
3. Or set the environment variable: CO_API_KEY=your_api_key_here
        """)
        sys.exit(1)

    try:
        client = cohere.Client(api_key=cohere_api_key)
        print("[green]Successfully connected to Cohere API![/green]")
        return client
    except Exception as e:
        print(f"[red]Error connecting to Cohere API: {str(e)}[/red]")
        sys.exit(1)


# Initialize the client
try:
    co = initialize_cohere_client()
except Exception as e:
    print(f"[red]Unexpected error: {str(e)}[/red]")
    sys.exit(1)

funcs = [
    "exit", "general", "realtime", "open", "close", "play",
    "generate image", "system", "content", "google search",
    "youtube search", "reminder"
]

messages = []

# Define preamble
preamble = """
You are a very accurate Decision-Making Model, which decides what kind of a query is given to you.
You will decide whether a query is a 'general' query, a 'realtime' query, or is asking to perform any task or automation like 'open facebook, instagram', 'can you write a application and open it in notepad'
*** Do not answer any query, just decide what kind of query is given to you. ***
-> Respond with 'general ( query )' if a query can be answered by a llm model (conversational ai chatbot) and doesn't require any up to date information like if the query is 'who was akbar?' respond with 'general who was akbar?', if the query is 'how can i study more effectively?' respond with 'general how can i study more effectively?', if the query is 'can you help me with this math problem?' respond with 'general can you help me with this math problem?', if the query is 'Thanks, i really liked it.' respond with 'general thanks, i really liked it.' , if the query is 'what is python programming language?' respond with 'general what is python programming language?', etc.
-> Respond with 'general (query)' if a query doesn't have a proper noun or is incomplete like if the query is 'who is he?' respond with 'general who is he?', if the query is 'what's his networth?' respond with 'general what's his networth?', if the query is 'tell me more about him.' respond with 'general tell me more about him.', and so on even if it require up-to-date information to answer.
-> Respond with 'general (query)' if the query is asking about time, day, date, month, year, etc like if the query is 'what's the time?' respond with 'general what's the time?'.
-> Respond with 'realtime ( query )' if a query can not be answered by a llm model (because they don't have realtime data) and requires up to date information like if the query is 'who is indian prime minister' respond with 'realtime who is indian prime minister', if the query is 'tell me about facebook's recent update.' respond with 'realtime tell me about facebook's recent update.', if the query is 'tell me news about coronavirus.' respond with 'realtime tell me news about coronavirus.', etc.
-> Respond with 'open (application name or website name)' if a query is asking to open any application like 'open facebook', 'open telegram', etc.
-> Respond with 'close (application name)' if a query is asking to close any application.
-> Respond with 'play (song name)' if a query is asking to play any song.
-> Respond with 'generate image (image prompt)' if a query is requesting to generate an image.
-> Respond with 'reminder (datetime with message)' if a query is requesting to set a reminder.
-> Respond with 'system (task name)' if a query is asking to mute, unmute, volume up, volume down.
-> Respond with 'content (topic)' if a query is asking to write any type of content.
-> Respond with 'google search (topic)' if a query is asking to search on google.
-> Respond with 'youtube search (topic)' if a query is asking to search on youtube.
*** If the query is asking to perform multiple tasks like 'open facebook, telegram and close whatsapp' respond with 'open facebook, open telegram, close whatsapp' ***
*** If the user is saying goodbye or wants to end the conversation like 'bye jarvis.' respond with 'exit'.***
*** Respond with 'general (query)' if you can't decide the kind of query or if a query is asking to perform a task which is not mentioned above. ***
"""

# Fixed chat history
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
    {"role": "User", "message": "do you like pizza?"},
    {"role": "Chatbot", "message": "general do you like pizza?"},
    {"role": "User", "message": "open chrome and tell me about mahatma gandhi?"},
    {"role": "Chatbot", "message": "open chrome, general tell me about mahatma gandhi"},
    {"role": "User", "message": "open chrome and firefox"},
    {"role": "Chatbot", "message": "open chrome, open firefox"},
    {"role": "User",
     "message": "what is today's date and by the way remind me that i have a dancing performance on 5th aug at 11pm"},
    {"role": "Chatbot", "message": "general what is today's date, reminder 11:00pm 5th aug dancing performance"}
]


def FirstlayerDMM(prompt: str = "test"):
    """Process user input and determine the appropriate response type."""
    try:
        # Add user query to message list
        messages.append({"role": "User", "message": prompt})

        # Create chat session with user
        stream = co.chat_stream(
            model="command-r-plus",
            message=prompt,
            temperature=0.7,
            chat_history=ChatHistory,
            prompt_truncation="OFF",
            connectors=[],
            preamble=preamble
        )

        response = ""
        for event in stream:
            if event.event_type == "text-generation":
                response += event.text

        # Clean and process response
        response = response.replace("\n", "")
        response = [task.strip() for task in response.split(",")]

        # Filter valid responses
        temp = []
        for task in response:
            for func in funcs:
                if task.lower().startswith(func):
                    temp.append(task)

        # Update chat history with bot's response
        ChatHistory.append({"role": "Chatbot", "message": ", ".join(temp)})

        if "(query)" in str(temp):
            return FirstlayerDMM(prompt=prompt)
        return temp

    except Exception as e:
        print(f"[red]Error processing request: {str(e)}[/red]")
        return ["error: " + str(e)]


if __name__ == "__main__":
    print("[yellow]Enter your queries (Ctrl+C to exit):[/yellow]")
    try:
        while True:
            user_input = input(">>> ")
            result = FirstlayerDMM(user_input)
            print(result)
    except KeyboardInterrupt:
        print("\n[yellow]Exiting...[/yellow]")
        sys.exit(0)