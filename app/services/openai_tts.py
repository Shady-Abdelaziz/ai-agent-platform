from openai import AsyncOpenAI

from app.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def generate_speech(text: str, output_path: str) -> str:
    """Convert text to speech and save to output_path. Returns the filename."""
    response = await client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    audio_data = response.content
    with open(output_path, "wb") as f:
        f.write(audio_data)
    # Return just the filename portion
    return output_path.split("/")[-1] if "/" in output_path else output_path.split("\\")[-1]
