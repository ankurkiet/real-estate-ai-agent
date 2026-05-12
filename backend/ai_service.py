from groq import Groq
import json
import os
import re

from knowledge_base import REAL_ESTATE_KNOWLEDGE
from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

INTENT_MODEL = "llama-3.1-8b-instant"
CHAT_MODEL = "openai/gpt-oss-120b"
EXTRACT_MODEL = "qwen/qwen3-32b"


# ─────────────────────────────────────────────
# GROQ CLIENT
# ─────────────────────────────────────────────

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ─────────────────────────────────────────────
# LOAD PROPERTY DATA
# ─────────────────────────────────────────────

_properties_path = os.path.join(
    os.path.dirname(__file__),
    "data",
    "properties.json"
)

with open(_properties_path, "r", encoding="utf-8") as f:
    PROPERTIES = json.load(f)


# ─────────────────────────────────────────────
# GENERIC LLM CALL
# ─────────────────────────────────────────────

def _call_llm(model, prompt, temperature=0):

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


# ─────────────────────────────────────────────
# CLEAN JSON RESPONSE
# ─────────────────────────────────────────────

def _extract_json_object(text):

    cleaned_text = re.sub(
        r"<think>.*?</think>",
        "",
        text,
        flags=re.DOTALL | re.IGNORECASE
    ).strip()

    cleaned_text = cleaned_text.replace("```json", "")
    cleaned_text = cleaned_text.replace("```", "")

    start_index = cleaned_text.find("{")
    end_index = cleaned_text.rfind("}")

    if start_index == -1 or end_index == -1:
        raise ValueError("No valid JSON object found")

    return json.loads(
        cleaned_text[start_index:end_index + 1]
    )


# ─────────────────────────────────────────────
# NORMALIZE VALUES
# ─────────────────────────────────────────────

def _parse_budget_value(value):

    if value is None:
        return None

    if isinstance(value, (int, float)):
        return int(value)

    if not isinstance(value, str):
        return value

    value = value.lower().replace(",", "").strip()

    crore_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(crore|cr)",
        value
    )

    if crore_match:
        return int(float(crore_match.group(1)) * 10000000)

    lakh_match = re.search(
        r"(\d+(?:\.\d+)?)\s*lakh",
        value
    )

    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)

    number_match = re.search(r"\d+(?:\.\d+)?", value)

    if number_match:
        return int(float(number_match.group(0)))

    return value


def _normalize_requirements(requirements):

    normalized = dict(requirements)

    if "budget" in normalized:
        normalized["budget"] = _parse_budget_value(
            normalized["budget"]
        )

    if normalized.get("bhk") is not None:

        try:
            normalized["bhk"] = int(normalized["bhk"])

        except:
            pass

    return normalized


# ─────────────────────────────────────────────
# INTENT DETECTION
# ─────────────────────────────────────────────

def detect_intent(user_message):

    prompt = f"""
    You are an intent classifier for a real estate AI assistant.

    Classify the message into ONLY one intent.

    Intents:

    property_search
    follow_up
    area_advice
    investment_advice
    market_info
    casual_chat

    Examples:

    "Show 3 BHK in Noida"
    → property_search

    "Anything cheaper?"
    → follow_up

    "Tell me about Sector 150"
    → area_advice

    "Is Noida good investment?"
    → investment_advice

    "Current Gurgaon property prices?"
    → market_info

    "Hello"
    → casual_chat

    Return ONLY the intent name.

    Message:
    {user_message}
    """

    intent = _call_llm(
        INTENT_MODEL,
        prompt
    )

    intent = intent.strip().lower()

    print("[INTENT]", intent)

    return intent


# ─────────────────────────────────────────────
# REAL ESTATE CHAT
# ─────────────────────────────────────────────

def real_estate_chat(user_message):

    prompt = f"""
    You are an expert Indian real estate consultant.

    Use:
    1. Real estate knowledge
    2. Available property listings

    to answer user questions professionally.

    REAL ESTATE KNOWLEDGE:
    {REAL_ESTATE_KNOWLEDGE}

    USER QUESTION:
    {user_message}

    IMPORTANT RULES:
    - Sound like experienced Indian real estate consultant
    - Keep responses VERY SHORT
    - Maximum 80 words
    - Prefer 3-5 bullet points
    - Give direct practical advice only
    - Avoid long explanations
    - Avoid repeating user question
    - Do not fabricate fake projects
    - Mention available listings only if relevant
    - Be mobile-friendly for Telegram chat
    """

    response = _call_llm(
        CHAT_MODEL,
        prompt,
        temperature=0.3
    )

    return response[:1000]


# ─────────────────────────────────────────────
# REQUIREMENT EXTRACTION
# ─────────────────────────────────────────────

def extract_requirements(
    user_message,
    previous_memory
):

    prompt = f"""
    You are a real estate AI assistant.

    Your task:
    - Understand current message
    - Understand previous memory
    - Return updated property requirements

    RULES:
    - Preserve old values unless changed
    - Update when user changes filter
    - Set value to null if removed
    - Return ONLY valid JSON
    - No explanation

    Previous Memory:
    {json.dumps(previous_memory)}

    User Message:
    {user_message}

    FINAL JSON FORMAT:

    {{
        "city": null,
        "location": null,
        "bhk": null,
        "budget": null,
        "purpose": null,
        "near_metro": null,
        "furnished": null,
        "parking": null,
        "property_type": null
    }}
    """

    text = _call_llm(
        EXTRACT_MODEL,
        prompt
    )

    requirements = _extract_json_object(text)

    return _normalize_requirements(
        requirements
    )