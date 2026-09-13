import os
from dotenv import load_dotenv
from google import genai

load_dotenv()   # <-- loads variables from .env

print("API Key loaded:", os.getenv("GEMINI_API_KEY") is not None)

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Explain Python decorators in simple terms."
)

print(response.text)