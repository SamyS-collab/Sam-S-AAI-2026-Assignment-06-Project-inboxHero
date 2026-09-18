# Roll Number: cert-aai-2026-06-0051

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. Add it to the .env file."
    )

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.5-flash-lite"

## MODEL_NAME = "gemini-3.6-flash"

## MODEL_NAME = "gemini-3.5-flash"



# maximum limit set for all Loops
MAX_ITERATIONS = 10

# Provider name
PROVIDER_NAME = ""