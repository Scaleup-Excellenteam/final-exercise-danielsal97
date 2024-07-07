import os
import openai
import asyncio

from flask.cli import load_dotenv


async def pptx_agent(input_text):
    """
    Communicates with OpenAI's GPT-3.5-turbo model to generate text based on the provided input.

    :param input_text: The text input to be processed by the AI model.
    :return: A list of generated text outputs.
    """
    response = await asyncio.to_thread(
        openai.ChatCompletion.create,
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Create paragraphs that explain this in hebrew:"},
            {"role": "user", "content": input_text}
        ]
    )
    output = [choice['message']['content'].strip() for choice in response.get('choices', [])
              if 'message' in choice and isinstance(choice['message'], dict) and choice['message'].get('content')]

    return output


def get_key():
    load_dotenv()
    env_key = os.getenv('OPENAI_API_KEY')
    if not env_key:
        print("API key not found. Please set it in the .env file.")
        exit(1)
    return env_key
