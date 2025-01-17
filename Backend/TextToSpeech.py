import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Get environment variables
env_vars = dotenv_values(".env")
assistant_voice = env_vars.get("AssistantVoice", "en-AU-NatashaNeural")


async def text_to_audio(text: str) -> None:
    """Convert text to audio file using edge-tts."""
    file_path = os.path.join("Data", "speech.mp3")

    # Clean up existing file
    if os.path.exists(file_path):
        os.remove(file_path)

    try:
        communicate = edge_tts.Communicate(
            text=text,
            voice=assistant_voice,
            pitch="+2Hz",
            rate="+10%"
        )
        await communicate.save(file_path)
    except Exception as e:
        print(f"Error in text_to_audio: {e}")
        raise


def tts(text: str, func=lambda r=None: True) -> bool:
    """Text to speech with pygame audio playback."""
    try:
        # Run async text to audio conversion
        asyncio.run(text_to_audio(text))

        # Initialize and play audio
        pygame.mixer.init()
        pygame.mixer.music.load(os.path.join("Data", "speech.mp3"))
        pygame.mixer.music.play()

        # Wait for playback to complete
        while pygame.mixer.music.get_busy():
            if func() is False:
                break
            pygame.time.Clock().tick(10)
        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")


# Enhanced responses with more variety and context
responses = [
    # Professional and direct
    "I've displayed the complete response on screen for your review.",
    "The full details are now available in the chat window.",
    "You'll find the complete information in the text display.",

    # Contextual transitions
    "As this is a detailed response, I've shown the full text on screen.",
    "For better readability, I've placed the complete explanation in the chat.",
    "Since this topic requires detail, you'll find the full response on screen.",

    # Action-oriented
    "Please refer to the chat window for the complete analysis.",
    "Take a moment to review the full details in the text display.",
    "You can find additional details by checking the chat window.",

    # Time-saving focused
    "For quick reference, I've displayed the complete text on screen.",
    "To save time, you can scan the full response in the chat window.",
    "The complete information is readily available in the text display.",

    # Informative
    "I've provided the comprehensive response in the chat window for your reference.",
    "The detailed explanation continues in the text display below.",
    "You'll find the in-depth analysis in the chat window.",

    # Technology-aware
    "The rest of the response is formatted for easy reading in the chat window.",
    "I've optimized the full response for viewing in the text display.",
    "The complete information is formatted for clarity in the chat.",

    # User-centric
    "To help you better understand, the full explanation is in the chat window.",
    "For your convenience, the complete response is displayed on screen.",
    "You can explore the full details at your own pace in the text display."
]


def text_to_speech(text: str, func=lambda r=None: True) -> None:
    """Process text and convert to speech with length handling."""
    sentences = str(text).split(".")

    # Check if text is long enough to split
    if len(sentences) > 4 and len(text) >= 250:
        first_part = ". ".join(sentences[:2]) + "."
        tts(first_part + " " + random.choice(responses), func)
    else:
        tts(text, func)


if __name__ == "__main__":
    # Create Data directory if it doesn't exist
    os.makedirs("Data", exist_ok=True)

    while True:
        try:
            user_input = input("Enter text: ")
            text_to_speech(user_input)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
