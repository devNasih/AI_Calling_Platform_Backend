import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

# This prompt can later be customized per campaign
DEFAULT_PROMPT_PREFIX = (
    "You are an AI calling agent helping a customer. Respond clearly and politely.\n\nUser: "
)

async def generate_response(transcript: str) -> str:
    try:
        prompt = DEFAULT_PROMPT_PREFIX + transcript

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=100,
            temperature=0.7,
        )

        return response["choices"][0]["message"]["content"].strip()

    except Exception as e:
        print(f"[GPT ERROR] {e}")
        return "I'm sorry, I didn't understand that."
 
