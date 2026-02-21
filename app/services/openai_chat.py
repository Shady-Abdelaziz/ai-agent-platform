from typing import List

from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_chat_response(messages: List[dict]) -> str:
    """Call OpenAI chat completions and return the assistant text."""
    response = await client.chat.completions.create(
        model="gpt-5.2",
        messages=messages,
    )
    return response.choices[0].message.content
