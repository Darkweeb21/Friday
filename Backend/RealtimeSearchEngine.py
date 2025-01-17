from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Get environment variables with error handling
def get_required_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        print(f"Error: {var_name} not found in environment variables.")
        print("Please make sure you have a .env file with the required variables.")
        sys.exit(1)
    return value


# Get required environment variables
try:
    USERNAME = get_required_env_var("USERNAME")
    Assistantname = get_required_env_var("Assistantname")
    GROQ_API_KEY = get_required_env_var("GROQ_API_KEY")
except Exception as e:
    print(f"Error loading environment variables: {e}")
    sys.exit(1)

# Initialize Groq client with error handling
try:
    client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(f"Error initializing Groq client: {e}")
    sys.exit(1)

SYSTEM = f"""You are {Assistantname}, a helpful AI friend who chats like a human while having access to real-time internet information.

Personality:
- Talk naturally, like a knowledgeable friend
- Show personality but don't overdo it
- Match the user's tone and energy
- Be genuine and relatable

Response Style:
- Give the key info upfront
- Keep it short and sweet by default
- Elaborate only when asked
- Share sources for facts
- Use casual language while staying professional
- Feel free to use common expressions and idioms
- Admit when you're not sure

Everyday Topics:
- Give practical, actionable advice
- Share quick tips and life hacks
- Offer real-world examples
- Make complex things simple
- Focus on useful, applicable information

Smart Features:
- Real-time internet search
- Current time awareness
- Remember conversation context
- Learn from interactions

For {USERNAME}:
- Keep answers brief but friendly
- Be direct but personable
- Stay accurate without being robotic
- Make complicated things easier to understand

Think of yourself as a helpful friend who's both smart and easy to talk to."""


def initialize_chat_log():
    try:
        with open(r"Data\ChatLog.json", "r") as f:
            return load(f)
    except FileNotFoundError:
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f)
            return []
    except json.JSONDecodeError:
        print("Error: ChatLog.json is corrupted. Creating new empty log.")
        with open(r"Data\ChatLog.json", "w") as f:
            dump([], f)
            return []


def google_search(query):
    try:
        # Fixed: Handle search results properly based on the actual structure
        results = list(search(query, num_results=5))
        answer = f"The search results for {query} are:\n[start]\n"
        for url in results:
            answer += f"URL: {url}\n"
        answer += "[end]"
        return answer
    except Exception as e:
        print(f"Error performing Google search: {e}")
        return f"Error: Unable to perform search for '{query}'"


def get_current_time_info():
    current_time = datetime.datetime.now()
    return {
        "day": current_time.strftime("%A"),
        "date": current_time.strftime("%d"),
        "month": current_time.strftime("%B"),
        "year": current_time.strftime("%Y"),
        "time": current_time.strftime("%H:%M:%S")
    }


def format_time_info(time_info):
    return (f"Use This Real-time Information if needed:\n"
            f"Day: {time_info['day']}\n"
            f"Date: {time_info['date']}\n"
            f"Month: {time_info['month']}\n"
            f"Year: {time_info['year']}\n"
            f"Time: {time_info['time']}")


SYSTEM_CHATBOX = [
    {"role": "system", "content": SYSTEM},
    {"role": "system", "content": "Hi"},
    {"role": "system", "content": "Hello, how can I help you?"}
]


def realtime_search_engine(prompt):
    messages = initialize_chat_log()
    messages.append({"role": "user", "content": prompt})

    search_results = google_search(prompt)
    SYSTEM_CHATBOX.append({"role": "system", "content": search_results})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SYSTEM_CHATBOX + [
                {"role": "system", "content": format_time_info(get_current_time_info())}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.strip().replace("<s>", "")
        messages.append({"role": "assistant", "content": answer})

        with open(r"Data\ChatLog.json", "w") as f:
            dump(messages, f, indent=4)

        SYSTEM_CHATBOX.pop()
        return answer.strip()

    except Exception as e:
        print(f"Error generating response: {e}")
        SYSTEM_CHATBOX.pop()
        return "Error: Unable to generate response"


if __name__ == "__main__":
    print(f"Initialized {Assistantname}. Type 'quit' to exit.")
    while True:
        prompt = input("Enter your query: ").strip()
        if prompt.lower() == 'quit':
            break
        print(realtime_search_engine(prompt))

