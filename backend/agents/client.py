import os
import json

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

INTENT_MODEL  = "llama-3.1-8b-instant"
CHAT_MODEL    = "openai/gpt-oss-120b"
EXTRACT_MODEL = "qwen/qwen3-32b"


# ─────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ─────────────────────────────────────────────
# PROPERTY DATA
# ─────────────────────────────────────────────

_properties_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data",
    "properties.json"
)

with open(_properties_path, "r", encoding="utf-8") as _f:
    PROPERTIES = json.load(_f)


# ─────────────────────────────────────────────
# GENERIC LLM CALL
# ─────────────────────────────────────────────

def call_llm(model, prompt, temperature=0):

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=temperature
    )

    return response.choices[0].message.content.strip()
