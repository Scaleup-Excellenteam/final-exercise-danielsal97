# openaiAgent.py

import openai
import asyncio


async def pptx_agent(input_text):
    """
    Communicates with OpenAI's GPT-3.5-turbo model to generate text based on the provided input.

    :param input_text: The text input to be processed by the AI model.
    :return: A list of generated text outputs.
    """
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Create paragraphs that explain this:"},
            {"role": "user", "content": input_text}
        ]
    )
    await asyncio.sleep(3)
    output = [choice['message']['content'].strip() for choice in response.get('choices', [])
              if 'message' in choice and isinstance(choice['message'], dict) and choice['message'].get('content')]

    return output
