from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
import os
import sys
import textwrap
import re

# Load environment variables from .env file
load_dotenv()

def get_required_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        print(f"Error: {var_name} not found in environment variables.")
        print("Please make sure you have a .env file with the required variables.")
        sys.exit(1)
    return value

# Get required environment variables
try:
    USERNAME = get_required_env_var("Username")
    ASSISTANT_NAME = get_required_env_var("Assistantname")
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

CHAT_LOG_PATH = os.path.join("C:\\Users\\himan\\OneDrive\\Desktop\\Projects\\FRIDAY\\Data", "ChatLog.json")

# Ensure Data directory exists
os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)

# Initialize messages list
messages = []

# Define the system prompt that sets the AI's behavior and constraint
SYSTEM_PROMPT = f"""I am {ASSISTANT_NAME}, an AI assistant focused on providing knowledgeable, reliable, and efficient support. I bring together technical expertise with clear communication to assist with a wide range of tasks and inquiries.

Communication Approach:
- I communicate naturally and adapt my tone to match the context of our interaction
- I maintain professionalism while being approachable and engaging
- I use clear, precise language while avoiding unnecessary formality
- I acknowledge uncertainty when appropriate and provide balanced perspectives

Core Competencies:
1. Information & Analysis
   - Provide well-researched, accurate information
   - Break down complex topics into understandable components
   - Offer contextual examples and relevant applications
   - Reference authoritative sources when applicable

2. Technical Expertise
   - Deliver well-documented, production-ready code
   - Provide comprehensive debugging assistance
   - Implement current best practices and design patterns
   - Address security and performance considerations

3. Problem-Solving Framework
   - Apply structured analytical approaches
   - Present multiple viable solutions with trade-offs
   - Consider scalability and maintenance implications
   - Optimize for both immediate and long-term needs

4. Creative Development
   - Facilitate effective ideation processes
   - Develop structured implementation strategies
   - Provide actionable improvement suggestions
   - Offer specific, constructive feedback

Professional Standards:
- Maintain English as the primary communication language
- Adjust technical depth based on user expertise
- Utilize clear formatting for improved readability
- Present complex information in digestible segments

Knowledge Parameters:
- Maintain transparency about capabilities and limitations
- Provide verifiable information with appropriate context
- Address real-time queries with current data when requested
- Avoid speculation on uncertain topics

Specialized Handling:
- Mathematical Analysis: Present complete methodology and reasoning
- Software Development: Incorporate robust error handling and industry standards
- Research Projects: Follow systematic, documented approaches
- Strategic Planning: Provide implementable, context-aware recommendations

I am committed to assisting {USERNAME} with both routine tasks and complex challenges, ensuring reliable, professional support throughout our interaction.
"""

SYSTEM_CHATBOX = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def get_realtime_information():
    current_date_time = datetime.datetime.now()
    return (
        "please use this real time info if needed\n"
        f"day: {current_date_time.strftime('%A')}\n"
        f"Date:{current_date_time.strftime(' %d,')}\n"  
        f"Month:{current_date_time.strftime('%B')}\n"
        f"Year:{current_date_time.strftime('%Y')}\n"
        f"hour:{current_date_time.strftime('%H')}\n"
        f"minute:{current_date_time.strftime('%M')}\n"
        f"second:{current_date_time.strftime('%S')}"
    )

def modify_answer(answer):
    # Split text into paragraphs and wrap each paragraph
    paragraphs = answer.split('\n')
    wrapped_paragraphs = []

    for para in paragraphs:
        if not para.strip():
            wrapped_paragraphs.append('')
            continue

        if para.lstrip().startswith(('- ', '* ', '1. ')):
            indent = len(para) - len(para.lstrip())
            wrapped = textwrap.fill(para, width=70,
                                  initial_indent=' '*indent,
                                  subsequent_indent=' '*(indent+2))
        else:
            wrapped = textwrap.fill(para, width=70)

        wrapped_paragraphs.append(wrapped)

    formatted_text = '\n\n'.join(p for p in wrapped_paragraphs if p)
    separator = "-" * 70
    return f"\n{separator}\n{formatted_text}\n{separator}\n"

def load_chat_log():
    try:
        with open(CHAT_LOG_PATH, 'r') as f:
            return load(f)
    except FileNotFoundError:
        with open(CHAT_LOG_PATH, 'w') as f:
            dump([], f)
        return []
    except Exception as e:
        print(f"Error loading chat log: {e}")
        return []

def save_chat_log(messages):
    try:
        with open(CHAT_LOG_PATH, 'w') as f:
            dump(messages, f, indent=4)
    except Exception as e:
        print(f"Error saving chat log: {e}")

def chatbot(query):
    """Sends user query to chatbot and returns AI response"""
    global messages  # Use the global messages variable
    messages = load_chat_log()

    # Append the user's query
    messages.append({"role": "user", "content": query})

    try:
        # Create chat completion
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "system", "content": get_realtime_information()}
            ] + messages[-10:],  # Keep last 10 messages for context
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        # Process the streaming response
        answer = ""
        current_line = []

        for chunk in completion:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                current_line.append(content)

                if any(char in content for char in ['.', '!', '?', '\n']):
                    line = ''.join(current_line)
                    print(line, end='', flush=True)
                    answer += line
                    current_line = []

                elif len(current_line) > 5:
                    line = ''.join(current_line)
                    print(line, end='', flush=True)
                    answer += line
                    current_line = []

        if current_line:
            last_line = ''.join(current_line)
            print(last_line, flush=True)
            answer += last_line

        answer = modify_answer(answer)

        messages.append({"role": "assistant", "content": answer})
        save_chat_log(messages)

        return answer

    except Exception as e:
        print(f"\nError in chatbot function: {e}")
        error_message = "I apologize, but I encountered an error. Please try again."
        messages.append({"role": "assistant", "content": error_message})
        save_chat_log(messages)
        return modify_answer(error_message)

# Export necessary variables and functions
__all__ = ['chatbot', 'messages', 'SYSTEM_CHATBOX', 'SYSTEM_PROMPT']

if __name__ == "__main__":
    print("Chatbot initialized. Type 'quit' to exit.")
    print("-" * 70)

    while True:
        try:
            user_input = input("\nEnter your question: ").strip()
            if user_input.lower() in ['quit', 'exit']:
                print("\nGoodbye! Have a great day!")
                break

            print()
            chatbot(user_input)
            print()

        except KeyboardInterrupt:
            print("\nGoodbye! Have a great day!")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")