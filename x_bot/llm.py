import os
from dotenv import load_dotenv
from litellm import completion

load_dotenv()

DEFAULT_PROMPT = "Write a tweet about: {topic}. Make it a banger!"

def get_llm_response(prompt: str = DEFAULT_PROMPT) -> str:
    """Get a response from the LLM."""
    if prompt == DEFAULT_PROMPT:
        import wonderwords
        topic = wonderwords.RandomWord().word(include_parts_of_speech=["nouns"])
        prompt = DEFAULT_PROMPT.format(topic=topic)
    response = completion(
                model="openrouter/google/gemini-2.0-flash-exp:free",
                messages=[{"role": "user", "content": prompt}]
            )
    return response['choices'][0]['message']['content']